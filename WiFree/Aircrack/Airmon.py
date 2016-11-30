import subprocess
import re

class Airmon:
    """
        Wrapper class for airmon-ng interface
    """

    AIRMON = "airmon-ng"
    AIRMON_START = "start"
    AIRMON_STOP = "stop"
    AIRMON_CHECK = "check"

    def __init__(self, interface):
        self._interface = interface
        self._monitorInterface = ""
        self.error = ""

    def getInterface(self):
        return self._interface

    def getMonitorInterface(self):
        return self._monitorInterface

    def start(self):
        # universal_newlines=True forces subprocess to return stdout and
        # stderr as strings and not as bytes
        p = subprocess.run([AIRMON, AIRMON_START, self._interface], \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                        check=True, universal_newlines=True)
        if p.stderr:
            self.error = p.stderr
            return False

        # searching for string "monitor mode enabled on"
        res = re.search('monitor mode enabled on (.*)', p.stdout)
        if res:
            iff = res.group(1)
            self._monitorInterface = iff[:-1]
        else:
            self.error = "couldn't find monitor interface"
            return False

    def stop(self):
        p = subprocess.run([AIRMON, AIRMON_STOP, self._monitorInterface], \
                        stdout=subprocess.PIPE                            \
                        check=True, universal_newlines=True)
        return True

    def check(self):
        p = subprocess.run([AIRMON, AIRMON_CHECK], stdout=subprocess.PIPE, \
                        check=True, universal_newlines=True)
        return p.stdout
