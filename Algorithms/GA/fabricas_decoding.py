import numpy as np


def plant_decoding(numberOfPlants, numberOfProducts, numberOfClients,
                   clientDemand, plantCapacity,depotCapacity, productionCost, V, A, C):

    # inputs
    V_c = V.copy()
    clientDemand_copy = clientDemand.copy()

     # 'closed' client
    for l in range(numberOfClients):
        if C[l] == 0:
            clientDemand_copy[l, :] = 0

    # output
    production = np.zeros((numberOfProducts, numberOfPlants))

    SumDepotCapacity = np.sum(depotCapacity)
    sumClientsDemands = np.sum(clientDemand_copy, axis=0)
    plantCapacity_c = plantCapacity.copy()
    productionCost_c = productionCost.copy()

    # Step 1: choose plant with highest priority, if there is still capacity and demand
    while SumDepotCapacity > 0  and np.sum(plantCapacity_c) and np.sum(sumClientsDemands) > 0 and max(V_c) > 0:
        j = np.argmax(V_c)
        r = int(A[j] - 1)

        # Step 2: decide amount of each product to be made in that plant, if there is still demand and capacity
        while plantCapacity_c[j] > 0 and SumDepotCapacity > 0 and np.amin(productionCost_c[r,:, j]) < np.inf:

            p = np.argmin(productionCost_c[r, :, j])  # min cost product
            production[p, j] = min(sumClientsDemands[p],  SumDepotCapacity, plantCapacity_c[j])  # min demand of p, plant capacity, sum of depot capacities and transportCap

            # Step 3: updateQuantities
            sumClientsDemands[p] = sumClientsDemands[p] - production[p, j]
            SumDepotCapacity = SumDepotCapacity - production[p, j]
            plantCapacity_c[j] = plantCapacity_c[j] - production[p, j]
            productionCost_c[r, p, j] = np.inf

        # change plants
        V_c[j] = 0

    return production
