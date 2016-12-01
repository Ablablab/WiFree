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
