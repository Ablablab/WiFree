import argparse
import sys
import os
import time
from WiFree.Settings.ConfigurationParser import ConfigurationParser
from WiFree.Settings.CurrentSettings import CurrentSettings
from WiFree.Settings import DEFAULT_CONFIG_FILE
from WiFree.Aircrack.Airmon import Airmon
from WiFree.Aircrack.Airodump import Airodump

parser = argparse.ArgumentParser(prog='wifree', description='Free your wifi.')
parser.add_argument('-e', '--essid', help='Network essid')
parser.add_argument('-i', '--interface', help='Network interface to put in     \
                                                monitor mode')
parser.add_argument('-f', '--file', help='Configuration file')
parser.add_argument('-w', '--whitelist', help='MAC whitelist, comma-separated')
parser.add_argument('-v', '--verbose', help='Verbosity on/off')

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
        VERBOSE = True

    if currentSettings.check_error():
        print("ERROR: some setting options are missing")
        print("please check bot the config file and the command line")
        exit(-1)

    if VERBOSE:
        print("Current settings: ")
        print("\tEssid: " + currentSettings.getEssid())
        print("\tInterface: " + currentSettings.getInterface())
        print("\tWhitelist: " + currentSettings.getWhitelist())

    airmon = Airmon(currentSettings.getInterface())

    if not airmon.start():
        print("ERROR: " + airmon.error)
        print("Aborting...")
        exit(-1)

    print("Activated monitor mode on interface " + airmon.getInterface())
    print("Monitor interface is " + airmon.getMonitorInterface())

    airodump = Airodump(airmon.getMonitorInterface(), \
                                        currentSettings.getEssid())
    if airodump.getBSSID(5, 2):
        print("Got MAC of closest AP with essid " + currentSettings.getEssid())
    else:
        print("Couldn't get BSSID for essid " + currentSettings.getEssid())
        print("Aborting...")
        airmon.stop()
        exit(-1)

    bssid = airodump._bssid

    airodump.start(["--bssid", bssid])
    print("Waiting for clients connected...")

    while True:
        time.sleep(5)

        airodump.read_res()
        clients = set(airodump._clients[currentSettings.getEssid()])
        whitelist = set(currentSettings.getWhitelist().split(" "))
        toDeauth = clients-whitelist

        if not toDeauth:
            print("No clients so far...")
            continue

        # TODO: deauthenticate clients in toDeauth list

    print("Deactivating monitor mode on interface " + airmon.getMonitorInterface())
    airmon.stop()
