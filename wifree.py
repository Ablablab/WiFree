import argparse
import sys
from WiFree.Settings.ConfigurationParser import ConfigurationParser
from WiFree.Settings.CurrentSettings import CurrentSettings, \
                                            DEFAULT_CONFIG_FILE

parser = argparse.ArgumentParser(prog='wifree', description='Free your wifi.')
parser.add_argument('-e', '--essid', help='Network essid')
parser.add_argument('-i', '--interface', help='Network interface to put in     \
                                                monitor mode')
parser.add_argument('-f', '--file', help='Configuration file')
parser.add_argument('-w', '--whitelist', help='MAC whitelist, comma-separated')

if __name__ == '__main__':
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

    if currentSettings.error:
        print("ERROR in configuration file ("+configFilePath+")")
        print("Make sure file syntax is correct and no field is missing")
        exit(-1)

    # Update configuration if new data is available on argv
    if args.essid:
        currentSettings.setEssid(args.essid)
    if args.interface:
        currentSettings.setInterface(args.interface)
    if args.whitelist:
        currentSettings.setWhitelist(" ".join(args.whitelist.split(",")))

    print("Current settings: ")
    print("Essid: " + currentSettings.getEssid())
    print("Interface: " + currentSettings.getInterface())
    print("Whitelist: " + currentSettings.getWhitelist())
