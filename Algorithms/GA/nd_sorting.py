import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def dominance(p, q,  fitness):
    #  returns True if p dominates q
    dominance = False
    if  fitness[p,0] <= fitness[q,0]:
        if fitness[p,1] <= fitness[q,1]:
            if fitness[p,2] >= fitness[q,2]:
                if fitness[p,2] != fitness[q,2] or fitness[p,0] != fitness[q,0] or fitness[p,1] != fitness[q,1]:
                    dominance = True

    return dominance


def nd_sorting(population, fitness, popSize):

    size = len(population)
    S = []
    N = []
    F =[]
    F1=[]
    rank = np.array(np.ones(size) *np.inf)
    count = 0

    for p in range(size):
        S_temp = []
        N_temp = 0
        for q in range(size):
            if q != p:
                if dominance(p, q, fitness) == True:
                    S_temp.append(q)
                elif dominance(q, p, fitness) == True:
                    N_temp = N_temp + 1

        S.append(S_temp)
        N.append(N_temp)
        if N_temp == 0:
            rank[p] = 1
            F1.append(p)
            count += 1

    F.append(F1)

    # other fronts
    i = 1
    F_temp = F1.copy()

    # continue sorting only until number of solutions is enough ( size of population). Discard the rest
    while len(F_temp)  != 0 and count < popSize:
        Q = []
        for p in F_temp:
            for q in S[p]:
                N[q] = N[q] - 1
                if N[q] == 0:
                    rank[q] = i + 1
                    Q.append(q)
                    count += 1


        i = i + 1
        F_temp = Q.copy()
        F.append(F_temp)

    return rank, F


def crowding_distance(set, fitness):

    n = len(set)
    distance = np.zeros((n))

    for m in range(len(fitness[1])):

        sort_fit = np.argsort(fitness[:, m])
        distance[sort_fit[0]] = np.inf
        distance[sort_fit[-1]] = np.inf
        for i in range(1, n-1):
            if (fitness[sort_fit[-1], m]- fitness[sort_fit[0], m]) != 0:
                distance[sort_fit[i]] =  distance[sort_fit[i]] + \
                                     (fitness[sort_fit[i+1], m] - fitness[sort_fit[i-1], m])/(fitness[sort_fit[-1], m]- fitness[sort_fit[0], m])

    return distance


def comparison(p, q, rank, crowding):

    #  returns best solution
    result = q
    if rank[p] < rank[q]:
        result = p
    elif rank[p] == rank[q]:
        if crowding[p] > crowding[q]:
            result = p

    return result

