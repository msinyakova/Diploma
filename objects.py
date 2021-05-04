

class Slices:
    def __init__(self, id_, speed, main_rate):
        self.sls_id = id_
        self.rate = speed
        self.bandwidth = main_rate

    def delay(self):
        return self.rate / self.bandwidth
