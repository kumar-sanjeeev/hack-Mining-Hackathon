class Target:
    def __init__(self, mac: int, offset, hint=""):
        self.__mac = mac
        self.__hint = hint
        self.__offset = offset

    def __eq__(self, other):
        if isinstance(other, Target):
            return self.__mac == other.__mac
        elif isinstance(other, int):
            return self.__mac == other
        return False

    def __hash__(self):
        return hash(self.__mac)

    def prepared_mac(self):
        return "{:012X}".format(self.__mac)

    @property
    def mac(self):
        return self.__mac

    @property
    def offset(self):
        return self.__offset

    @property
    def hint(self):
        return self.__hint

    def __repr__(self):
        return "{:012X}".format(self.__mac)

    def __str__(self):
        return "{:012X}".format(self.__mac)  # {self.__hint}


class Anchor(Target):
    def __init__(self, target, x, y):
        super(Anchor, self).__init__(target.mac, target.offset, target.hint)
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __repr__(self):
        return "{} @ ({:3.1f}|{:3.1f})".format(self.prepared_mac(),
                                               self.x,
                                               self.y)


class Result(Target):
    def __init__(self, target, distance, rssi, took_s):
        super(Result, self).__init__(target.mac, target.offset, target.hint)
        self.__distance = distance
        self.__rssi = rssi
        self.__took = took_s

    @property
    def distance(self):
        return self.__distance - self.offset

    @property
    def rssi(self):
        return self.__rssi

    @property
    def took(self):
        return self.__took

    def __str__(self):
        return "{} -> {} cm @ {} dbm / {:.1f} ms".format(self.prepared_mac(), self.distance, self.rssi, 1000 * self.took)
