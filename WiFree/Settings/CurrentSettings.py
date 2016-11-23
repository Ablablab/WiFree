# default configuration file path
DEFAULT_CONFIG_FILE="config.txt"
# strings for settings
CONFIG_ESSID='essid'
CONFIG_INTERFACE='interface'
CONFIG_WHITELIST='whitelist'
# class CurrentSettings
# used to keep in memory current program settings
class CurrentSettings:
    def __init__(self, settings):
        self.settings = {}
        self.error = False
        # We are sure settings contain all needed data because we always call
        # this after ConfigurationParser, but checking for robustness
        if not CONFIG_ESSID in settings or                                     \
                not CONFIG_INTERFACE in settings or                            \
                not CONFIG_WHITELIST in settings:
            self.error = True
            return None
        self.settings = settings

    def getValue(self, what):
        if what in self.settings:
            return self.settings[what]

    def setValue(self, what, value):
        if what in self.settings:
            self.settings[what] = value

    def getEssid(self):
        return self.settings[CONFIG_ESSID]

    def getInterface(self):
        return self.settings[CONFIG_INTERFACE]

    def getWhitelist(self):
        return self.settings[CONFIG_WHITELIST]

    def setEssid(self, essid):
        self.settings[CONFIG_ESSID] = essid

    def setInterface(self, iff):
        self.settings[CONFIG_INTERFACE] = iff

    def setWhitelist(self, whitelist):
        self.settings[CONFIG_WHITELIST] = whitelist
