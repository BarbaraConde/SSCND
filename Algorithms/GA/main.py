import numpy as np
import random
from funcoes import functions
from operadores import crossover, mutation, zero_mutation
from nd_sorting import crowding_distance, nd_sorting, comparison
from time import time


# set time
strTime = time()

# read model parameters from csv
# sets
numberOfPlants, numberOfTransportTypes, numberOfProducts, numberOfClients, numberOfDepots, \
numberOfRawM, numberOfPeriods, numberOfRoutes = np.genfromtxt(
    'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/conjuntosGA.csv', dtype=int)

# Environmental
transportEmissions = np.genfromtxt(
    'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/transportEmission.csv', delimiter=';')
productionEmissions = np.genfromtxt(
    'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/productionEmission.csv',
    delimiter=';')

# Technical
clientDemand = np.zeros((numberOfPeriods, numberOfClients, numberOfProducts))
for period in range(numberOfPeriods):
    clientDemand[period, :, :] = np.genfromtxt(
        'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/demand.csv', delimiter=';',
        max_rows=numberOfClients,
        skip_header=1 + (numberOfClients + 1) * (period))

billOfMaterials = np.zeros((numberOfRoutes, numberOfRawM, numberOfProducts))
for route in range(numberOfRoutes):
    billOfMaterials[route, :, :] = np.genfromtxt(
        'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/boM.csv', delimiter=';',
        max_rows=numberOfRawM,
        skip_header=1 + (numberOfRawM + 1) * route)

plantMaxCapacity = np.genfromtxt(
    'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/plantMaxCapacity.csv', delimiter=';')
plantMinCapacity = np.genfromtxt(
    'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/plantMinCapacity.csv', delimiter=';')
depotMaxCapacity = np.genfromtxt(
    'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/depotMaxCapacity.csv', delimiter=';')
depotMinCapacity = np.genfromtxt(
    'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/depotMinCapacity.csv', delimiter=';')

distanceJtoK = np.zeros((numberOfTransportTypes, numberOfPlants, numberOfDepots))
for tipo in range(numberOfTransportTypes):
    distanceJtoK[tipo, :, :] = np.genfromtxt(
        'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/jToK.csv', delimiter=';',
        max_rows=numberOfPlants,
        skip_header=1 + (numberOfPlants + 1) * tipo)

distanceKtoL = np.zeros((numberOfTransportTypes, numberOfDepots, numberOfClients))
for tipo in range(numberOfTransportTypes):
    distanceKtoL[tipo, :, :] = np.genfromtxt(
        'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/kToL.csv', delimiter=';',
        max_rows=numberOfDepots,
        skip_header=1 + (numberOfDepots + 1) * tipo)

# Financial
penalty = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/penalty.csv', delimiter=';')
openDepotCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/openDepot.csv',
                               delimiter=';')
openPlantCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/openPlant.csv',
                               delimiter=';')
EstPlantCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/estPlant.csv',
                              delimiter=';')
EstDepotCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/estDepot.csv',
                              delimiter=';')
transportCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/transportCost.csv',
                               delimiter=';')

productionCost = np.zeros((numberOfRoutes, numberOfProducts, numberOfPlants))
for route in range(numberOfRoutes):
    productionCost[route, :, :] = np.genfromtxt(
        'C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/productionCost.csv',
        delimiter=';',
        max_rows=numberOfProducts,
        skip_header=1 + (numberOfProducts + 1) * route)

rawMaterialCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/rawMaterialCost.csv',
                                 delimiter=';')

#  Social
ivsPlant = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/ivsPlant.csv', delimiter=';')
ivsDepot = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/M1/ivsDepot.csv', delimiter=';')

# set GA parameters
np.random.seed(99)
random.seed(99)
popSize = 100
maxCount = 20

# initial constants
generation = 1
firstLength = numberOfPlants + numberOfDepots
totalLength = (3 * (numberOfPlants + numberOfDepots) + numberOfClients)
population = np.zeros((popSize, numberOfPeriods, totalLength))

# Initial Population
for x in range(1,popSize):

    for j in range(numberOfPlants):
        # open plants

        population[x, :, j] = random.randint(0, numberOfRoutes)
        # capacities
        population[x, :, numberOfPlants + numberOfDepots + j] = random.random()
    for k in range(numberOfDepots):
        # open depots
        population[x, :, k + numberOfPlants] = random.randint(0, 1)
        # capacities
        population[x, :, 2 * numberOfPlants + numberOfDepots + k] = random.random()

    for t in range(numberOfPeriods):
        sequence = list(range(1, numberOfPlants + numberOfDepots + numberOfClients + 1))
        for y in range(firstLength * 2, totalLength):
            number = random.choice(sequence)
            sequence.remove(number)
            population[x, t, y] = number


popVariables = []
popObjectives = []
count = 0

#  Decode population
for n in range(popSize):

        # decode solution
        decoding = functions(population[n, :, :], numberOfPlants, numberOfTransportTypes, numberOfProducts,
                             numberOfClients, numberOfDepots, numberOfRawM, numberOfPeriods, numberOfRoutes,
                             transportEmissions,
                             productionEmissions, clientDemand, billOfMaterials, plantMaxCapacity, plantMinCapacity,
                             depotMaxCapacity, depotMinCapacity,
                             distanceJtoK, distanceKtoL, penalty, openDepotCosts, openPlantCosts, EstPlantCosts,
                             EstDepotCosts, transportCosts,
                             productionCost, rawMaterialCosts, ivsPlant, ivsDepot)
        count = count + 1

        popVariables.append(decoding[0])  # save variables

        # save values
        popObjectives.append(decoding[1])

popObjectives = np.array(list(popObjectives))

# Save best solutions
bestEco = min(popObjectives[:,0])
bestEnv = min(popObjectives[:,1])
bestSoc = max(popObjectives[:,2])
print(bestEco, bestEnv, bestSoc)

#  Calculate fitness and sort population
sorting = nd_sorting(population, popObjectives, popSize)
rank = sorting[0]
front = sorting[1]
distance = crowding_distance(population, popObjectives)

#  Main Loop
bestCounter = 0
while bestCounter <= maxCount:
    mutationProb = 0.4
    pm = bestCounter/maxCount
    if pm >= mutationProb:
        mutationProb = pm

    offspring = np.zeros((popSize, numberOfPeriods, totalLength))
    y = 0
    while y < popSize:  # generate new population of size N

        #  Choose parents
        parents = np.zeros((2, numberOfPeriods, totalLength))
        parentOne, parentTwo = [], []
        for a in range(2):
            parentOne.append(random.randint(0, popSize - 1))
            parentTwo.append(random.randint(0, popSize - 1))

        # choose best parent by crowding distance and non dominance
        parents[0, :, :] = population[comparison(parentOne[0], parentOne[1], rank, distance)]
        parents[1, :, :] = population[comparison(parentTwo[0], parentTwo[1], rank, distance)]

        #  Crossover
        cross = crossover(parents[0, :, :], parents[1, :, :], numberOfPlants, numberOfDepots, numberOfPeriods)
        offspring[y, :, :] = cross[0, :, :]
        offspring[y + 1, :, :] = cross[1, :, :]

        #  Mutation with some probability
        randNumber = random.random()
        if randNumber < mutationProb:
            offspring[y, :, :] = mutation(offspring[y, :, :], numberOfPlants, numberOfDepots, numberOfPeriods)
        #if randNumber < mutationProb/2:
         #   offspring[y, :, :] = zero_mutation(offspring[y, :, :])

        randNumber2 = random.random()
        if randNumber2 < mutationProb:
            offspring[y + 1, :, :] = mutation(offspring[y + 1, :, :], numberOfPlants, numberOfDepots, numberOfPeriods)
        #if randNumber2 < mutationProb/2:
            #offspring[y + 1, :, :] = zero_mutation(offspring[y + 1, :, :])
        y += 2

    #  add offspring to population
    new_population = np.zeros((2 * popSize, numberOfPeriods, totalLength))
    new_population[0:popSize, :, :] = population
    new_population[popSize::, :, :] = offspring[:, :, :]

    # decode offspring
    newPopVariables = []
    newPopObjectives = []

    for n in range(popSize, 2 * popSize):
        # check if solution has already been decoded

        # check_list = np.all(allSolutions == new_population[n, :, :], axis=(1, 2))
        # if np.any(check_list):
        #     x = list(check_list).index(True)
        #
        #     # add decoded values to current solution
        #     newPopObjectives.append(allObjectives[x])
        #     newPopVariables.append(allVariables[x])
        #
        # else:
        # decode solution and add it to the list

        # decode solution
        decoding = functions(new_population[n, :, :], numberOfPlants, numberOfTransportTypes, numberOfProducts,
                                 numberOfClients, numberOfDepots, numberOfRawM, numberOfPeriods, numberOfRoutes,
                                 transportEmissions, productionEmissions, clientDemand, billOfMaterials,
                                 plantMaxCapacity, plantMinCapacity, depotMaxCapacity, depotMinCapacity,
                                 distanceJtoK, distanceKtoL, penalty, openDepotCosts, openPlantCosts, EstPlantCosts,
                                 EstDepotCosts, transportCosts, productionCost, rawMaterialCosts, ivsPlant, ivsDepot)
        count = count + 1


        newPopVariables.append(decoding[0])  # save variables

         # save values
        newPopObjectives.append(decoding[1])

    # updates objectives and variables matrix
    twoPopObjectives = np.zeros((2 * popSize, 3))
    twoPopObjectives[0:popSize, :] = popObjectives[:, :]
    twoPopObjectives[popSize::, :] = np.array(list(newPopObjectives))[:, :]

    twoPopVariables = []
    twoPopVariables.extend(popVariables)
    twoPopVariables.extend(newPopVariables)

    # sort new population
    sorting = nd_sorting(new_population, twoPopObjectives, popSize)
    rank = sorting[0]
    front = sorting[1]

    # cut the N worst individuals:
    populationIndex = []
    newRank = []
    newDistance = []
    i = 0

    # append best fronts
    while len(populationIndex) + len(front[i]) <= popSize:

        # add all individuals from this front to new solution
        populationIndex.extend(front[i])
        newRank.extend([rank[i] for i in front[i]])

        currentFront = [new_population[x] for x in front[i]]
        frontFitness = [twoPopObjectives[x] for x in front[i]]
        currentFront = np.array(list(currentFront))
        frontFitness = np.array(list(frontFitness))

        # calculate crowding distance for the front
        distance = crowding_distance(currentFront, frontFitness)
        newDistance.extend(distance)

        i = i + 1
        if len(front) >= i:
            break

    # If front has more individuals than there are spaces left in the population, cut using crowding distance
    if len(populationIndex) < popSize:
        currentFront = [new_population[x] for x in front[i]]
        frontFitness = [twoPopObjectives[x] for x in front[i]]
        currentFront = np.array(list(currentFront))
        frontFitness = np.array(list(frontFitness))

        distance = crowding_distance(currentFront, frontFitness)
        while len(populationIndex) < popSize:
            bestIndex = np.argmax(distance)

            # add solution to population
            populationIndex.append(front[i][bestIndex])

            # add solution rank
            newRank.append(rank[front[i][bestIndex]])

            # add solution crowding distance
            newDistance.append(distance[bestIndex])

            distance[bestIndex] = 0

    #  Update population
    population[:, :, :] = [new_population[n, :, :] for n in populationIndex]
    popObjectives[:, :] = [twoPopObjectives[n, :] for n in populationIndex]
    popVariables = [twoPopVariables[n] for n in populationIndex]
    rank = np.array(list(newRank))
    distance = np.array(list(newDistance))

    # update best solutions

    minEco = min(popObjectives[:, 0])
    minEnv = min(popObjectives[:, 1])
    maxSoc = max(popObjectives[:, 2])


    if minEco < bestEco:
        bestEco = minEco
        bestCounter = -1
    if minEnv < bestEnv:
        bestEnv = minEnv
        bestCounter = -1
    if maxSoc > bestSoc:
        bestSoc = maxSoc
        bestCounter = -1

    generation += 1
    bestCounter += 1

# return results
print(f'The number of function calls was {count}, in {round(time() - strTime, 2)} seconds')

import csv

with open('results_novo/output_M1_99_obj.csv', mode='w') as output_obj:
    writer = csv.writer(output_obj, delimiter=';')
    for row in popObjectives:
        writer.writerow(row)

with open('results_novo/output_M1_99_var.csv', mode='w') as output_var:
    writer_v = csv.writer(output_var, delimiter=';')
    for row in popVariables:
        writer_v.writerow(row)

with open('results_novo/output_M1_99_pop.csv', mode='w') as output_pop:
    writer_p = csv.writer(output_pop, delimiter=';')
    for row in population:
        writer_p.writerow(row)



