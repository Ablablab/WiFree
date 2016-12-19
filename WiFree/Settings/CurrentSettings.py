from . import CONFIG_ESSID, CONFIG_INTERFACE, CONFIG_WHITELIST
# class CurrentSettings
# used to keep in memory current program settings
class CurrentSettings:
    def __init__(self, settings):
        self.settings = {}
        self.error = False
        self.settings = settings

    def check_error(self, others):
        for o in others:
            if not o in self.settings:
                return True
        if not CONFIG_ESSID in self.settings or \
                not CONFIG_INTERFACE in self.settings or \
                not CONFIG_WHITELIST in self.settings:
            return True
        else:
            return False


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
