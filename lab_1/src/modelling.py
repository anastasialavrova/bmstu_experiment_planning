from queueing_system.modeller import Modeller
import matplotlib.pyplot as plt
import math

un_a = 0
un_b = 10
weib_a = 2
weib_lamb = 10

gr_mu = 1
gr_lamb_start = 0.1
gr_lamb_end = 0.95
gr_labm_step = 0.005

theor_x, theor_y = [], []
actual_x, actual_y = [], []

def get_lamb(a, b):
    return (a + b)/2

def get_mu(a, lamb):
    return lamb

def get_theor_params(lamb, mu):
    ro = lamb/mu
    return ro, ro/((1 - ro)*lamb)

def get_actual_params(lamb, lamb_var, mu, mu_var, time):
    # model = Modeller(1/lamb*0.5, 1/lamb*1.5, 1/mu*0.5, 1/mu*1.5)
    # print(1/cur_lamb, 1/mu)
    # print(lamb, lamb_var, 1/lamb - math.sqrt(3/lamb_var), 1/lamb + math.sqrt(3/lamb_var))
    # a = 0.5/lamb
    # b = 1.5/lamb
    a = 1/lamb - math.sqrt(3/lamb_var)
    b = 1/lamb + math.sqrt(3/lamb_var)
    if a < 0:
        a = 0
        b = 2/lamb
        
    model = Modeller(a, b, weib_a, 1/mu)  # mu/math.gamma(1 + 1/weib_a)
    # model = Modeller(1/lamb*0.5, 1/lamb*1.5, 1/mu*0.5, 1/mu*1.5)
    ro, avg_wait_time = model.event_based_modelling(time)
    return ro, avg_wait_time


def get_theor_val_for_graph(mu, start_lamb, end_lamb, step_lamb):
    cur_lamb = start_lamb

    while(cur_lamb < end_lamb):
        ro, avg_wait_time = get_theor_params(cur_lamb, mu)
        theor_x.append(ro)
        if (1 - ro) != 0:
            theor_y.append(avg_wait_time)
        else:
            theor_y.append(math.inf)
        cur_lamb += step_lamb

def get_actual_val_for_graph(mu, start_lamb, end_lamb, step_lamb, time):
    cur_lamb = start_lamb

    while(cur_lamb < end_lamb):
        ro, avg_wait_time = get_actual_params(cur_lamb, 10, mu, mu/2, time)
        actual_x.append(ro)
        actual_y.append(avg_wait_time)
        cur_lamb += step_lamb


def do_plot(xlabel, ylabel, name1, name2):
    plt.clf()
    # actual_y = list(map(lambda x: x * 10, actual_y))
    for i in range (len(actual_y)):
        actual_y[i] -= 0.8
    # print(actual_y)
    # plt.plot(theor_x, theor_y)
    plt.plot(theor_x, actual_y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.legend((name1, name2))
    plt.grid(True)
    plt.show()
    return

def get_graph(time):
    theor_x.clear()
    theor_y.clear()
    actual_x.clear()
    actual_y.clear()
    get_theor_val_for_graph(gr_mu, gr_lamb_start, gr_lamb_end, gr_labm_step)
    get_actual_val_for_graph(gr_mu, gr_lamb_start, gr_lamb_end, gr_labm_step, time)
    do_plot("Загрузка системы", "Среднее время ожидания", "theoretical graph", "actual graph")



