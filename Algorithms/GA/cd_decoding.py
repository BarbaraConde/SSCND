import numpy as np


def cd_decoding(numberOfPlants, numberOfDepots, numberOfProducts, transportTypes, depotCapacity, plantSupply,
                costMatrix, V):


    depotCapacityC = depotCapacity.copy()
    plantSupplyC = plantSupply.copy()
    costMatrixC = costMatrix.copy()
    V_c = V.copy()

    shippedProduct = np.zeros((transportTypes, numberOfProducts, numberOfPlants, numberOfDepots))

    while max(V_c) > 0  and np.amin(costMatrixC) < np.inf:

        k = np.argmax(V_c)  # select highest priority Depot

        min_soruce = np.where(costMatrixC[:, :, k] == np.amin(costMatrixC[:, :, k]))  # min cost transport type and plant

        s = min_soruce[0][0]  # min cost transport type
        j = min_soruce[1][0]  # min cost plant

        p = 0  # loop through each product

        while depotCapacityC[k] > 0 and max(plantSupplyC[:, j]) > 0  and p < numberOfProducts:

            shippedProduct[s, p, j, k] = min(depotCapacityC[k], plantSupplyC[p, j])

            depotCapacityC[k] = depotCapacityC[k] - shippedProduct[s, p, j, k]
            plantSupplyC[p, j] = plantSupplyC[p, j] - shippedProduct[s, p, j, k]
            p = p + 1


        if depotCapacityC[k] == 0:  # clear empty nodes
            V_c[k] = 0
            costMatrixC[:, :, k] = np.inf

        if np.sum(plantSupplyC[:, j]) == 0:
            costMatrixC[:, j, :] = np.inf

    return shippedProduct

