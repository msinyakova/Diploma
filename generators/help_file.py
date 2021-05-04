class myTime :
    def __init__(self, string = '') :
        self.elem = str(string)
        self.list = self.parsing(str(string)).copy()

    def __add__(self, string) :
        self.elem += ('_' + str(string))
        self.list.extend(self.parsing(str(string)))
        return self.elem

    def __getitem__(self, key) :
        if type(key) == int:
            return self.list[key]
        if type(key) == slice:
            result = ""
            start = 0 if key.start == None else key.start
            stop = len(self.list) if key.stop == None else key.stop
            step = 1 if key.step == None else key.step
            while start < stop :
                result += self.list[start] + '_'
                start += step
            return result

    def __str__(self) :
        return self.elem

    def parsing(self, string) :
        words = list()
        elem = ''
        for char in string :
            if char != '_' :
                elem += char
            else :
                words.append(elem)
                elem = ''
        words.append(elem)
        return words

a = myTime("65")
print(a)
c = myTime("123_23_3")
print(c[1:])