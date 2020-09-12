class DynamicDataIdentifier:
    def __init__(self, dynamic_data, name):
        self.dynamic_data = dynamic_data
        self.name = name
        self.index = None

    def get(self):
        if type(self.index) == int:
            return self.dynamic_data.get(self.name)[self.index]
        else:
            return self.dynamic_data.get(self.name)

    def __getitem__(self, key):
        self.index = key
        return self

    def __setitem__(self, key, value):
        self.dynamic_data.__dict__[self.name][key] = value

    def __delitem__(self, key):
        del self.dynamic_data[self.name][key]


class DynamicData:
    names = list()

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        DynamicData.names.append(name)

    def __getattribute__(self, name):
        if name in DynamicData.names:
            DynamicData.temp = DynamicDataIdentifier(self, name)
            return DynamicData.temp
        else:
            return super(DynamicData, self).__getattribute__(name)

    def __getattr__(self, name):
        DynamicData.temp = DynamicDataIdentifier(self, name)
        return DynamicData.temp

    def get(self, name):
        return self.__dict__[name]


d = DynamicData()
