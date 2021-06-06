from fabricas_decoding import plant_decoding
from cd_decoding import cd_decoding
from clientes_decoding import client_decoding
import numpy as np


def decoding(numberOfPlants, numberOfTransportTypes, numberOfProducts, numberOfClients, numberOfDepots,
             numberOfPeriods, numberOfRoutes, clientDemand,plantMaxCapacity, plantMinCapacity, depotMaxCapacity,
             depotMinCapacity, distanceJtoK, distanceKtoL, transportCosts, productionCost, V):

    # Inputs
    clientDemand_copy = clientDemand.copy()
    V_copy = V.copy()
    transportCostJtoK = np.zeros((numberOfTransportTypes, numberOfPlants, numberOfDepots))
    transportCostKtoL = np.zeros((numberOfTransportTypes, numberOfDepots, numberOfClients))

    for s in range(numberOfTransportTypes):
        transportCostJtoK[s,:,:] = distanceJtoK[s,:,:] * transportCosts[s]
        transportCostKtoL[s,:,:] = distanceKtoL[s,:,:] * transportCosts[s]

    # variables
    backDemand = np.zeros((numberOfPeriods + 1, numberOfProducts, numberOfClients))
    shippedProductToDepots = np.zeros(
        (numberOfPeriods, numberOfTransportTypes, numberOfProducts, numberOfPlants, numberOfDepots))
    shippedProductToClient = np.zeros(
        (numberOfPeriods, numberOfTransportTypes, numberOfProducts, numberOfDepots, numberOfClients))
    production = np.zeros((numberOfPeriods, numberOfProducts, numberOfPlants))
    establishedPlants = np.zeros((numberOfPlants, numberOfRoutes))
    establishedDepots = np.zeros(numberOfDepots)
    openPlants = np.zeros((numberOfPeriods, numberOfPlants))
    openDepots = np.zeros((numberOfPeriods, numberOfDepots))
    plantCapacity = np.zeros((numberOfPeriods, numberOfPlants))
    depotCapacity = np.zeros((numberOfPeriods, numberOfDepots))
    capVarPlantsUp = np.zeros((numberOfPeriods, numberOfPlants, numberOfRoutes))
    capVarPlantsLo = np.zeros((numberOfPeriods, numberOfPlants, numberOfRoutes))
    capVarDepotsUp = np.zeros((numberOfPeriods, numberOfDepots))
    capVarDepotsLo = np.zeros((numberOfPeriods, numberOfDepots))

    # Calculate capacities and variations
    for t in range(numberOfPeriods):
        for j in range(numberOfPlants):

            rota = int(V_copy[0, j] - 1)
            factor = V_copy[t, numberOfPlants + numberOfDepots + j]
            if rota >= 0:
                plantCapacity[t,j] = plantMinCapacity[rota] + (plantMaxCapacity[rota] - plantMinCapacity[rota]) * factor
                capVar = plantCapacity[t,j] - plantCapacity[t-1, j]
                if capVar > 0:
                    capVarPlantsUp[t,j,rota] = capVar
                else:
                    capVarPlantsLo[t,j,rota] = abs(capVar)

        for k in range(numberOfDepots):
            factor = V_copy[t, 2*numberOfPlants + numberOfDepots + k]
            depotCapacity[t, k] = depotMinCapacity + (depotMaxCapacity - depotMinCapacity) * factor
            capVar = depotCapacity[t, k] - depotCapacity[t - 1, k]
            if capVar > 0:
                capVarDepotsUp[t, k] = capVar
            else:
                capVarDepotsLo[t, k] = abs(capVar)


    for k in range(numberOfDepots):
        # closed depot, priority = 0
        if V_copy[0, k + numberOfPlants] == 0:
            depotCapacity[:,k] = 0
            capVarDepotsUp[:,k] = 0
            capVarDepotsLo[:,k] = 0
            V_copy[:, (3 * numberOfPlants) + 2*numberOfDepots + k] = 0
        else:
            establishedDepots[k] = 1

    for j in range(numberOfPlants):
        rota = int(V_copy[0, j])
        if rota == 0:
            #closed plant
            plantCapacity[:,j] = 0
            capVarPlantsLo[:,j, rota] = 0
            capVarPlantsUp[:,j, rota] = 0
            V_copy[:, 2*(numberOfPlants + numberOfDepots) + j] = 0
        else:
            establishedPlants[j, rota-1] = 1

    # Start
    t = 1

    # loop for every period
    while t < (numberOfPeriods + 1):

        # Update inventories and demand
        for p in range(numberOfProducts):
            clientDemand_copy[t - 1, :, p] = clientDemand_copy[t - 1, :, p] + backDemand[t - 1, p, :]

        # Part 1: Plants
        production[t - 1, :, :] = plant_decoding(numberOfPlants, numberOfProducts, numberOfClients,
                                        clientDemand[t-1, :, :], plantCapacity[t-1, :],depotCapacity[t-1, :], productionCost,
                                        V_copy[t - 1, 2*(numberOfPlants + numberOfDepots):(2* (numberOfPlants + numberOfDepots) + numberOfPlants )],
                                        V_copy[t - 1, 0:numberOfPlants],
                                        V_copy[t - 1, (3 * (numberOfPlants + numberOfDepots)):len(V[0])])


        # Part 2: Depots

        shippedProductToDepots[t - 1, :, :, :, :] = cd_decoding(numberOfPlants, numberOfDepots, numberOfProducts, numberOfTransportTypes,
                                    depotCapacity[t-1, :], production[t - 1, :, :], transportCostJtoK,
                                    V_copy[t - 1,
                                    (3 * numberOfPlants + 2*numberOfDepots):(3 * (numberOfPlants + numberOfDepots))])


        depotInventory = np.sum(np.sum(shippedProductToDepots[t - 1, :, :, :, :], axis=0), axis=1)

        # part 3: Clients
        shippedProductToClient[t - 1, :, :, :, :] = client_decoding(numberOfClients, numberOfDepots, numberOfProducts, numberOfTransportTypes,
                                          depotInventory[:, :], clientDemand_copy[t - 1, :, :], transportCostKtoL,
                                          V_copy[t - 1, (3 * (numberOfPlants + numberOfDepots)):(
                                                  3* (numberOfPlants + numberOfDepots) + numberOfClients)])


        # Update

        for p in range(numberOfProducts):
            backDemand[t, p, :] = clientDemand_copy[t - 1, :, p] - np.sum(
                np.sum(shippedProductToClient[t - 1, :, p, :, :], axis=0), axis=0)

        for j in range(numberOfPlants):
            if V_copy[t - 1, 2*(numberOfPlants + numberOfDepots) + j] != 0:
                openPlants[t - 1, j] = 1

        for k in range(numberOfDepots):
            if V_copy[t - 1, (3*numberOfPlants + 2*numberOfDepots) + k] != 0:
                openDepots[t - 1, k] = 1

        t = t + 1

    return backDemand, shippedProductToDepots, shippedProductToClient, production, establishedPlants, establishedDepots,\
           openPlants, openDepots, capVarPlantsUp,capVarPlantsLo, capVarDepotsUp, capVarDepotsLo
