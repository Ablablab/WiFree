# class ConfigurationParser
# read and parse configuration file
class ConfigurationParser:
    settings = {}

    def __init__(self, path):
        self.path = path

    def readConfiguration(self):
        # try to open the file
        try:
            f = open(self.path, 'r')
        # return false on error
        except IOError, err:
            return False
        # if open is successful, parse the file
        else:
            self.__readConfiguration(f)
            # finally close the file
            f.close()
        return True

    def __readConfiguration(self, file):
        for line in file:
            keyval = line.split("=")
            try:
                self.settings[keyval[0].rstrip()] = keyval[1].rstrip()
            except IndexError:
                continue

    def getConfiguration(self):
        return self.settings
