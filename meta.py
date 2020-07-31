class DynamicDataIdentifier:
    def __init__(self, name):
        self.name = name

    def get(self):
        return d.get(self.name)


class DynamicData:
    names = list()

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        DynamicData.names.append(name)

    def __getattribute__(self, name):
        if name in DynamicData.names:
            return DynamicDataIdentifier(name)
        else:
            return super(DynamicData, self).__getattribute__(name)

    def __getattr__(self, name):
        return DynamicDataIdentifier(name)

    def get(self, name):
        return self.__dict__[name]


d = DynamicData()
