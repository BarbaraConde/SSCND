import numpy as np
#from NSGAII_Novo.decoding import decoding
from decoding import decoding

def functions(V, numberOfPlants, numberOfTransportTypes, numberOfProducts, numberOfClients, numberOfDepots,numberOfRawM, numberOfPeriods, numberOfRoutes, transportEmissions,
productionEmissions, clientDemand, billOfMaterials, plantMaxCapacity, plantMinCapacity, depotMaxCapacity, depotMinCapacity,
distanceJtoK, distanceKtoL, penalty, openDepotCosts, openPlantCosts, EstPlantCosts, EstDepotCosts,transportCosts,
productionCost, rawMaterialCosts, ivsPlant, ivsDepot):

    # decode chromosome to get variables


    variablesMatrix = decoding(numberOfPlants, numberOfTransportTypes, numberOfProducts, numberOfClients, numberOfDepots,
             numberOfPeriods, numberOfRoutes, clientDemand,plantMaxCapacity, plantMinCapacity, depotMaxCapacity,
             depotMinCapacity, distanceJtoK, distanceKtoL, transportCosts, productionCost, V)

    # variables
    backDemand = variablesMatrix[0]
    shippedProductToDepots = variablesMatrix[1]
    shippedProductToClient = variablesMatrix[2]
    production = variablesMatrix[3]
    establishedPlants = variablesMatrix[4]
    establishedDepots = variablesMatrix[5]
    openPlants = variablesMatrix[6]
    openDepots = variablesMatrix[7]
    capVarPlantsUp = variablesMatrix[8]
    capVarPlantsLo = variablesMatrix[9]
    capVarDepotsUp = variablesMatrix[10]
    capVarDepotsLo = variablesMatrix[11]


    objective1 = 0
    objective2 = 0
    objective3 = 0

    for t in range(numberOfPeriods):

        # Penalty Costs
        for l in range(numberOfClients):
            for p in range(numberOfProducts):
                objective1 = objective1 + penalty[p] * backDemand[t+1, p, l]

        #  Buying raw materials
        for m in range(numberOfRawM):
            for p in range(numberOfProducts):
                for j in range(numberOfPlants):
                    r = int(V[t, j] - 1)
                    if r > -1:
                        for r in range(numberOfRoutes):
                            if establishedPlants[j, r] == 1:
                                objective1 = objective1 + rawMaterialCosts[t, m] * billOfMaterials[r, m, p] * production[t, p, j]

        #  Production Costs and Emissions
        for p in range(numberOfProducts):
            for j in range(numberOfPlants):
                r = int(V[t, j] - 1)
                if r > -1:
                    # if plant has that route
                    if establishedPlants[j, r] == 1:
                        objective1 = objective1 + productionCost[r, p, j] * production[t, p, j]

                        objective2 = objective2 + productionEmissions[r] * production[t, p, j]


        #  Maintaining facilities Costs
        for j in range(numberOfPlants):
            r = int(V[t, j] - 1)
            if r > -1:
                if establishedPlants[j, r] == 1:
                    objective1 = objective1 + openPlants[t, j] * openPlantCosts[j, r]

        for k in range(numberOfDepots):
            objective1 = objective1 + openDepots[t, k] * openDepotCosts[k]

        #  transport Costs and Emissions
        for p in range(numberOfProducts):
            for k in range(numberOfDepots):
                for l in range(numberOfClients):
                    for s in range(numberOfTransportTypes):

                        objective1 = objective1 + transportCosts[s] * distanceKtoL[s, k, l] * \
                                     shippedProductToClient[
                                         t, s, p, k, l]
                        objective2 = objective2 + transportEmissions[s] * shippedProductToClient[t, s, p, k, l] * \
                                     distanceKtoL[s, k, l]


        for p in range(numberOfProducts):
            for j in range(numberOfPlants):
                for k in range(numberOfDepots):
                    for s in range(numberOfTransportTypes):
                        objective1 = objective1 + transportCosts[s] * distanceJtoK[s, j, k] * \
                                     shippedProductToDepots[
                                         t, s, p, j, k]
                        objective2 = objective2 + transportEmissions[s] * shippedProductToDepots[t, s, p, j, k] * \
                                     distanceJtoK[s, j, k]

        #  Capacity Variations
        for j in range(numberOfPlants):
            for r in range(numberOfRoutes):
                if establishedPlants[j, r] == 1:
                    objective1 += (capVarPlantsUp[t, j, r] - capVarPlantsLo[t, j, r]) * EstPlantCosts[r]

        for k in range(numberOfDepots):
            if establishedDepots[k] == 1:
                objective1 += (capVarDepotsUp[t, k] - capVarDepotsLo[t, k]) * EstDepotCosts

        #  IVS
        for j in range(numberOfPlants):
            objective3 = objective3 + production[t, :, j].sum() * ivsPlant[j]

        for k in range(numberOfDepots):
            objective3 = objective3 + shippedProductToDepots[t, :, :, :, k].sum() * ivsDepot[k]

    # Establishing Facilities costs
    for j in range(numberOfPlants):
        for r in range(numberOfRoutes):
            objective1 = objective1 + establishedPlants[j, r] * plantMinCapacity[r] * EstPlantCosts[r]

    for k in range(numberOfDepots):
        objective1 = objective1 + establishedDepots[k] * depotMinCapacity * EstDepotCosts

    objectives = [objective1, objective2, objective3]

    return variablesMatrix, objectives
