import numpy as np
import itertools as it


def calc_n(factors_amount):
    return 2 ** factors_amount


def calc_exp_amount(factors_amount, n):
    return n + 2 * factors_amount + 1


def calc_star_length(n, exp_amount):
    print(exp_amount)
    return (((n * exp_amount) ** 0.5 - n) / 2) ** 0.5


def calc_star_shift(n, exp_amount):
    return (n / exp_amount) ** 0.5


def combination(factors):
    res = list()
    for length in range(2, len(factors) + 1):
        for subset in it.combinations(factors, length):
            res.append(np.prod(subset))
    return res


def shifted_points(factors, a):
    res = list()
    for f in factors:
        res.append(f ** 2 - a)
    return res


def fill_factors(plan, factors_amount, n):
    step = 1
    for j in range(factors_amount):
        sign = -1
        for i in range(n):
            plan[i][j + 1] = sign
            if (i + 1) % step == 0:
                sign *= -1
        step *= 2


def fill_star_sides(plan, factors_amount, n, exp_amount):
    sign = -1
    factori = 0
    d = calc_star_length(n, exp_amount)
    for i in range(n, exp_amount - 1):
        factors = [0] * factors_amount
        factors[factori] = sign * d
        plan[i].extend(factors)
        if sign == 1:
            factori += 1
            sign = -1
        else:
            sign = 1


def fill_star_center(plan, factors_amount, n, exp_amount):
    a = calc_star_shift(n, exp_amount)
    plan[exp_amount - 1].extend([0] * (n - 1))
    plan[exp_amount - 1].extend([-a] * factors_amount)


def matrix_plan(factors_amount):
    n = calc_n(factors_amount)
    exp_amount = calc_exp_amount(factors_amount, n)
    res = [[1 for i in range(1 + factors_amount)] for j in range(n)]
    res.extend([[1 for i in range(1)] for j in range(exp_amount - n)])

    fill_factors(res, factors_amount, n)
    fill_star_sides(res, factors_amount, n, exp_amount)
    fill_star_center(res, factors_amount, n, exp_amount)

    a = calc_star_shift(n, exp_amount)
    for i in range(exp_amount - 1):
        res[i].extend(combination(res[i][1:factors_amount + 1]))
        res[i].extend(shifted_points(res[i][1:factors_amount + 1], a))

    return res


def calc_b(plan, y):
    b = list()
    for i in range(len(plan[0])):
        xy = xx = 0
        for j in range(len(plan)):
            xy += plan[j][i] * y[j]
            xx += plan[j][i] ** 2
        b.append(xy / xx)
    return b


def calc_y(b, x):
    res = 0
    for i in range(len(b)):
        res += b[i] * x[i]
    return res


def fill_y(plan, b):
    ycalc = list()
    for i in range(len(plan)):
        if len(plan[i]):
            ycalc.append(calc_y(b, plan[i]))
    return ycalc


def fill_plan(plan, y, ycalc):
    for i in range(len(plan)):
        if len(plan[i]):
            plan[i].append(y[i])
            plan[i].append(ycalc[i])
            plan[i].append(abs(y[i] - ycalc[i]))


def expand_plan(plan, custom_plan, y):
    b = calc_b(plan, y)

    ycalc = fill_y(plan, b)
    fill_plan(plan, y, ycalc)
    ycalc = fill_y(custom_plan, b)
    if len(custom_plan) > 0:
        fill_plan(custom_plan, y[len(plan):], ycalc)

    return b


def scale_factor(x, realmin, realmax, xmin=-1, xmax=1):
    return realmin + (realmax - realmin) * (x - xmin) / (xmax - xmin)
