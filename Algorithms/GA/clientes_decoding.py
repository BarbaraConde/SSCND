import numpy as np


def client_decoding(numberOfClients, numberOfDepots, numberOfProducts, transportTypes, depotInventory, ClientDemand,
                    costMatrix,  V):
    depotCapacityC = depotInventory.copy()
    clientDemandC = ClientDemand.copy()
    costMatrixC = costMatrix.copy()
    V_c = V.copy()

    shippedProduct = np.zeros((transportTypes, numberOfProducts, numberOfDepots, numberOfClients))

    while max(V_c) > 0:
        # Step1: Choose client
        l = np.argmax(V_c)

        # deciding transportation from Cd to clients

        while max(clientDemandC[l, :]) > 0  and np.amin(costMatrixC[:, :, l]) < np.inf:

            min_transp = np.where(costMatrixC[:, :, l] == np.amin(costMatrixC[:, :, l]))
            s = min_transp[0][0]  # min cost transport type
            k = min_transp[1][0]  # Cd

           # if s == 0:
            #    if costMatrixC[s, k, l] != 0.0:
             #       print("erro")

            p = 0
            while max(clientDemandC[l, :]) > 0 and max(depotCapacityC[:, k]) > 0 and p < numberOfProducts:
                shippedProduct[s, p, k, l] = min(clientDemandC[l, p],  depotCapacityC[p, k])

                # updateQuantities
                clientDemandC[l, p] = clientDemandC[l, p] - shippedProduct[s, p, k, l]
                depotCapacityC[p, k] = depotCapacityC[p, k] - shippedProduct[s, p, k, l]

                p = p + 1

            if np.sum(clientDemandC[l,
                      :]) == 0:  # client demand has been satisfied, client does not receive anything else
                costMatrixC[:, :, l] = np.inf

            if np.sum(depotCapacityC[:, k]) == 0:  # depot has no more products, can't deliver anything else
                costMatrixC[:, k, :] = np.inf

            costMatrixC[:, k, l] = np.inf  # depot k can't satisfy client l demand anymore (loop broke)

        V_c[l] = 0  # go to next client

    return shippedProduct


