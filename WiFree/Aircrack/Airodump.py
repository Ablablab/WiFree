import os
import time
from subprocess import Popen, DEVNULL

class Airodump:
    """
        Wrapper class for airodump-ng
    """

    AIRODUMP = "airodump-ng"

    def __init__(self, miff, essid):
        # set monitor interface
        self._miff = miff
        # set essid
        self._essid = essid
        # bssid station
        self._bssid = ''
        # bssid and channel list of stations with essid matching _essid
        self._aps = {}
        # bssid-essid list. It's the same as above, used for usefulness
        self._bssids = {}
        # clients bssid list
        self._clients = {}
        # default file for airodump output
        self._airout = "airout"
        # variable to hold the status of the airodump process
        self._running = False
        # variable to hold the number of executions
        self._n = 0

    def getBSSID(self, sec, max):
        """
            Gets the bssid of the closest ap with essid _essid
            @sec: seconds to wait before choosing the closest ap
            @max: max number of attempts of sec seconds before aborting
        """

        if self._running:
            return False

        self.start([])

        i = 0
        while not self._essid in self._aps:
            if (i == max):
                return False
            time.sleep(sec)
            self.read_res()
            i += 1

        self.stop()
        self._bssid = self._aps[self._essid][0]
        return True

    def stop(self):
        if self._running:
            self._running = False
            return self._proc.kill()
        else:
            return False

    def start(self, args):
        # if it's already running, don't do anything
        if self._running:
            return False

        # build airodump flags
        flags = args

        if '--write' not in flags:
            flags.extend(["--write", self._airout])
        if '--output-format' not in flags:
            flags.extend(["--output-format", "csv"])

        # filter airodump output to remove unassociated clients
        if '-a' not in flags:
            flags.extend(["-a"])

        # build Popen command as list
        cmd = [self.AIRODUMP] + flags + [self._miff]

        # start the process
        # use Popen because subprocess.run waits for the process to complete
        # while Popen starts the process and then returns. We need airodump
        # running in background while analyzing the result
        self._proc = Popen(cmd,env={'PATH': os.environ['PATH']}, \
                               stderr=DEVNULL, stdin=DEVNULL, stdout=DEVNULL)

        self._running = True
        self._n += 1

    def read_res(self):
        n = str(self._n).zfill(2)
        f = open(self._airout+"-"+n+".csv")
        # remove whitespaces/newline/ etc...
        stripped = [l.strip() for l in f.readlines()]
        # remove empty lines
        lines = [a for a in stripped if a]

        aps = []
        clients = []

        self._aps = {}
        self._bssids = {}
        self._clients = {}

        n = 0
        for line in lines:
            n += 1
            # this line identifies the beginning of the BSSIDs
            if line.startswith('BSSID'):
                continue
            # this line identifies the beginning of the clients
            if line.startswith('Station'):
                n += 1
                break
            aps.append(line)

        for line in lines[n:]:
            clients.append(line)

        # get essid/bssid of each station
        for ap in aps:
            ap = ap.split(",")
            a = [v.strip() for v in ap]
            essid = a[-2]
            bssid = a[0]
            if essid in self._aps:
                self._aps[essid].append(bssid)
            else:
                self._aps[essid] = [bssid]
            self._bssids[bssid] = essid

        # get MAC address of clients connected to each station
        for cl in clients:
            cl = cl.split(",")
            c = [v.strip() for v in cl]
            client_mac = c[0]
            ap_mac = c[5]

            if ap_mac.startswith('(not associated)'):
                continue
            essid = self._bssids[ap_mac]
            if essid in self._clients:
                self._clients[essid].append(client_mac)
            else:
                self._clients[essid] = [client_mac]
