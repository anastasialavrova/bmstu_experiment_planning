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
    def __init__(self, generators, proc_modes, total_apps=0):
        self.generators = generators
        self.processors = proc_modes
        self.total_apps = total_apps

    def proceed(self):
        processed = 0
        self.queue = []
        self.events = []
        self.totally_waited = 0
        for i in range(len(self.generators)):
            self.events.append([self.generators[i].generation_time(), 'g', i])
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
        self.queue.append((event[0], event[2]))
        self._add_event([event[0] + self.generators[event[2]].generation_time(), 'g', event[2]])
        if self.free:
            self._process(event[0])

    def _process(self, time):
        if len(self.queue) > 0:
            app_time, app_type = self.queue.pop(0)
            processing_time = self.processors[app_type].generation_time()
            self.totally_waited += processing_time + time - app_time
            self._add_event([time + processing_time, 'p'])
            self.free = False
        else:
            self.free = True
