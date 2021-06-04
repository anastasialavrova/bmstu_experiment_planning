import numpy as np


def matrix_plan():
    res = [[1 for i in range(8)] for j in range(8)]
    step = 1
    for j in range(3):
        sign = -1
        for i in range(8):
            res[i][j + 1] = sign
            if (i + 1) % step == 0:
                sign *= -1
        step *= 2
    for i in range(8):
        res[i][4] = res[i][1] * res[i][2]
        res[i][5] = res[i][1] * res[i][3]
        res[i][6] = res[i][2] * res[i][3]
        res[i][7] = res[i][1] * res[i][2] * res[i][3]
    return res


def calc_xmat(plan):
    transposed = np.transpose(plan)
    mat = np.matmul(transposed, np.array(plan))
    mat = np.linalg.inv(mat)
    mat = np.matmul(mat, transposed)
    return mat.tolist()


def linear(b, x):
    res = 0
    linlen = int(np.log2(len(b))) + 1
    for i in range(linlen):
        res += b[i] * x[i]
    return res


def nonlinear(b, x):
    res = 0
    for i in range(len(b)):
        res += b[i] * x[i]
    return res


def expand_plan(plan, custom_plan, y, xmat):
    b = list()
    for i in range(len(xmat)):
        b_cur = 0
        for j in range(len(xmat[i])):
            b_cur += xmat[i][j] * y[j]
        b.append(b_cur)

    for i in custom_plan:
        if len(i) > 0:
            plan.append(i.copy())

    ylin = list()
    ynlin = list()
    for i in range(len(plan)):
        ylin.append(linear(b, plan[i]))
        ynlin.append(nonlinear(b, plan[i]))

    for i in range(len(plan)):
        plan[i].append(y[i])
        plan[i].append(ylin[i])
        plan[i].append(ynlin[i])
        plan[i].append(abs(y[i] - ylin[i]))
        plan[i].append(abs(y[i] - ynlin[i]))

    return plan, b


def scale_factor(x, realmin, realmax, xmin=-1, xmax=1):
    print(realmin + (realmax - realmin) * (x - xmin) / (xmax - xmin))
    return realmin + (realmax - realmin) * (x - xmin) / (xmax - xmin)
