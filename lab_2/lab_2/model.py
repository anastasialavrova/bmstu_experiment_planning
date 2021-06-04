from numpy.random import exponential, normal


def exp_by_intensity(params):
    return exponential(1 / params[0])


def norm_by_intensity(params):
    res = -1
    while res < 0:
        res = normal(1 / params[0], 1 / params[1])
    return res


class Generator:
    def __init__(self, func, params):
        self.law = func
        self.params = params

    def generation_time(self):
        return self.law(self.params)


class EventModel:
    def __init__(self, generators, processor, total_apps=0):
        self.generators = generators
        self.processor = processor
        self.total_apps = total_apps

    def proceed(self):
        processed = 0
        self.queue = []
        self.events = []
        self.totally_waited = 0
        i = 0
        for generator in self.generators:
            self.events.append([generator.generation_time(), 'g', 0])
            i += 1
        self.free = True
        while processed < self.total_apps:
            event = self.events.pop(0)
            if event[1] == 'g':
                self._generate(event)
            elif event[1] == 'p':
                processed += 1
                self._process(event[0])

        return self.totally_waited

    def _add_event(self, event: list):
        i = 0
        while i < len(self.events) and self.events[i][0] < event[0]:
            i += 1
        self.events.insert(i, event)

    def _generate(self, event):
        self.queue.append(event[0])
        self._add_event([event[0] + self.generators[event[2]].generation_time(), 'g', event[2]])
        if self.free:
            self._process(event[0])

    def _process(self, time):
        if len(self.queue) > 0:
            processing_time = self.processor.generation_time()
            self.totally_waited += processing_time + time - self.queue.pop(0)
            self._add_event([time + processing_time, 'p'])
            self.free = False
        else:
            self.free = True

