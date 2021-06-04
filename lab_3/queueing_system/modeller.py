from .distribution import Uniform, Weibull, Normal
from .generator import Generator
from .processor import Processor


class Modeller:
    def __init__(self, uniform_a1, uniform_b1, uniform_a2, uniform_b2, weibull_a, weibull_lamb, m):
        self._generator_1 = Generator(Uniform(uniform_a1, uniform_b1))
        self._generator_2 = Generator(Uniform(uniform_a2, uniform_b2))
        self._processor = Processor(Normal(weibull_a, weibull_lamb))
        self._generator_1.add_receiver(self._processor)
        self._generator_2.add_receiver(self._processor)

    def event_based_modelling(self, end_time):
        generator_1 = self._generator_1
        generator_2 = self._generator_2
        processor = self._processor 

        gen_period_1 = generator_1.next_time()
        gen_period_2 = generator_2.next_time()
        proc_period = min(gen_period_1, gen_period_2) + processor.next_time()

        start_times = []
        end_times = []
        print(gen_period_1, gen_period_2, proc_period)

        cur_time = 0
        queue = 0               

        while cur_time < end_time:
            if gen_period_1 <= proc_period and gen_period_1 < gen_period_2:
                start_times.append(gen_period_1)
                generator_1.emit_request()
                gen_period_1 += generator_1.next_time()
                cur_time = gen_period_1
                # print('a', gen_period_1, gen_period_2, proc_period)
            if gen_period_2 <= proc_period and gen_period_1 > gen_period_2:
                start_times.append(gen_period_2)
                generator_2.emit_request()
                gen_period_2 += generator_2.next_time()
                cur_time = gen_period_2
                # print('b', gen_period_1, gen_period_2, proc_period)

            if gen_period_1 >= proc_period or gen_period_2 >= proc_period:
                end_times.append(proc_period)
                processor.process()
                if processor.current_queue_size > 0:
                    time = processor.next_time()
                    proc_period += time
                    # print('c', gen_period_1, gen_period_2, proc_period, time)
                else:
                    time = processor.next_time()
                    proc_period = min(gen_period_1, gen_period_2) + time
                    # print('d', gen_period_1, gen_period_2, proc_period, time)
                cur_time = proc_period
                
        
        avg_wait_time = 0
        # print("len start and ena times", len(start_times), len(end_times))
        request_count = min(len(end_times), len(start_times))

        tmp = []
        for i in range(request_count):
            avg_wait_time += end_times[i] - start_times[i]
            tmp.append(end_times[i] - start_times[i])
        
        if request_count > 0:
            avg_wait_time /= request_count
        # print("start_times", start_times)
        # print("end_times", end_times)
        # print(tmp)

        actual_lamb_1 = self._generator_1.get_avg_intensity()
        actual_lamb_2 = self._generator_2.get_avg_intensity()
        actual_mu = self._processor.get_avg_intensity()
        ro = (actual_lamb_1 + actual_lamb_2)/2/actual_mu
        # print("actual_ro", actual_lamb_1, actual_lamb_2, actual_mu)

        return ro, avg_wait_time

    def time_based_modelling(self, request_count, dt):
        generator = self._generator
        processor = self._processor

        gen_period = generator.next_time()
        proc_period = gen_period + processor.next_time()
        current_time = 0

        while processor.processed_requests < request_count:
            if gen_period <= current_time:
                generator.emit_request()
                gen_period += generator.next_time()
            if current_time >= proc_period:
                processor.process()
                if processor.current_queue_size > 0:
                    proc_period += processor.next_time()
                else:
                    proc_period = gen_period + processor.next_time()
            current_time += dt

        return (processor.processed_requests, processor.reentered_requests,
                processor.max_queue_size, round(current_time, 3))
