import gurobipy as gp
from gurobipy import GRB
import numpy as np
from time import time

strTime = time()
# Read data from csv files
# Sets
numberOfPlants, numberOfTransportTypes, numberOfProducts, numberOfClients, numberOfDepots, \
numberOfRawM, numberOfPeriods, numberOfRoutes = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/conjuntos.csv', dtype=int)

numberOfPlants, numberOfTransportTypes, numberOfProducts, numberOfClients, numberOfDepots, \
numberOfRawM, numberOfPeriods, numberOfRoutes = numberOfPlants.item(), \
                                                numberOfTransportTypes.item(), numberOfProducts.item(), \
                                                numberOfClients.item(), numberOfDepots.item(), \
                                                numberOfRawM.item(), numberOfPeriods.item(), numberOfRoutes.item()

# Environmental
transportEmissions = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/transportEmission.csv', delimiter=';')
productionEmissions = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/productionEmission.csv',
                                    delimiter=';')

# Technical
clientDemand = np.zeros((numberOfPeriods, numberOfClients, numberOfProducts))
for period in range(1,numberOfPeriods):
    clientDemand[period, :, :] = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/demand.csv', delimiter=';',
                                               max_rows=numberOfClients,
                                               skip_header=1 + (numberOfClients + 1) * (period-1))

billOfMaterials = np.zeros((numberOfRoutes, numberOfRawM, numberOfProducts))
for route in range(numberOfRoutes):
    billOfMaterials[route, :, :] = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/boM.csv', delimiter=';',
                                                 max_rows=numberOfRawM,
                                                 skip_header=1 + (numberOfRawM + 1) * route)

plantMaxCapacity = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/plantMaxCapacity.csv', delimiter=';')
plantMinCapacity = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/plantMinCapacity.csv', delimiter=';')
depotMaxCapacity = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/depotMaxCapacity.csv', delimiter=';')
depotMinCapacity = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/depotMinCapacity.csv', delimiter=';')


distanceJtoK = np.zeros((numberOfTransportTypes, numberOfPlants, numberOfDepots))
for tipo in range(numberOfTransportTypes):
    distanceJtoK[tipo, :, :] = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/jToK.csv', delimiter=';',
                                             max_rows=numberOfPlants,
                                             skip_header=1 + (numberOfPlants + 1) * tipo)

distanceKtoL = np.zeros((numberOfTransportTypes, numberOfDepots, numberOfClients))
for tipo in range(numberOfTransportTypes):
    distanceKtoL[tipo, :, :] = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/kToL.csv', delimiter=';',
                                             max_rows=numberOfDepots,
                                             skip_header=1 + (numberOfDepots + 1) * tipo)

# Financial
penalty = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/penalty.csv', delimiter=';')
openDepotCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/openDepot.csv', delimiter=';')
openPlantCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/openPlant.csv', delimiter=';')
EstPlantCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/estPlant.csv', delimiter=';')
EstDepotCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/estDepot.csv', delimiter=';')
transportCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/transportCost.csv', delimiter=';')

productionCost = np.zeros((numberOfRoutes, numberOfProducts, numberOfPlants))
for route in range(numberOfRoutes):
    productionCost[route, :, :] = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/productionCost.csv',
                                                delimiter=';',
                                                max_rows=numberOfProducts,
                                                skip_header=1 + (numberOfProducts + 1) * route)

rawMaterialCosts = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/rawMaterialCost.csv', delimiter=';')

#  Social
ivsPlant = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/ivsPlant.csv', delimiter=';')
ivsDepot = np.genfromtxt('C:/Users/Barbara/PycharmProjects/Dissertacao/NSGAII_Novo/data/ivsDepot.csv', delimiter=';')

# Create optimization model and set solving parameters
model = gp.Model('MultiObjetivo')
#model.Params.timeLimit = 100
model.Params.MIPGap = 0.005
#model.Params.SolFiles = "out"


# Create variables

backDemand = model.addMVar((numberOfPeriods, numberOfProducts, numberOfClients), vtype=GRB.CONTINUOUS, lb=0.0,
                       name="backDemand")

shippedProductToDepots = model.addMVar(
    (numberOfPeriods, numberOfTransportTypes, numberOfProducts, numberOfPlants, numberOfDepots), vtype=GRB.CONTINUOUS,
    lb=0.0, name="shippedProductToDepots")
shippedProductToClient = model.addMVar(
    (numberOfPeriods, numberOfTransportTypes, numberOfProducts, numberOfDepots, numberOfClients), vtype=GRB.CONTINUOUS,
    lb=0.0, name="shippedProductToClient")

production = model.addMVar((numberOfPeriods, numberOfProducts, numberOfPlants,numberOfRoutes), vtype=GRB.CONTINUOUS, lb=0.0,
                       name="production")

establishedPlants = model.addMVar((numberOfPlants, numberOfRoutes), vtype=GRB.BINARY, name="establishedPlants")
establishedDepots = model.addMVar((numberOfDepots), vtype=GRB.BINARY, name="establishedDepots")
openPlants = model.addMVar((numberOfPeriods, numberOfPlants, numberOfRoutes), vtype=GRB.BINARY, name="openPlants")
openDepots = model.addMVar((numberOfPeriods, numberOfDepots), vtype=GRB.BINARY, name="openDepots")

capVarPlantsUp = model.addMVar((numberOfPeriods, numberOfPlants, numberOfRoutes), vtype=GRB.CONTINUOUS, lb=0.0, name="capVarPlantsUp")
capVarPlantsLo = model.addMVar((numberOfPeriods, numberOfPlants, numberOfRoutes), vtype=GRB.CONTINUOUS, lb=0.0, name="capVarPlantsLo")
capVarDepotsUp = model.addMVar((numberOfPeriods, numberOfDepots), vtype=GRB.CONTINUOUS, lb=0.0, name="capVarDepotsUp")
capVarDepotsLo = model.addMVar((numberOfPeriods, numberOfDepots), vtype=GRB.CONTINUOUS,lb=0.0, name="capVarDepotsLo")


plantCapacity = model.addMVar((numberOfPeriods, numberOfPlants, numberOfRoutes), vtype=GRB.CONTINUOUS, lb=0.0, name="plantCapacity")
depotCapacity = model.addMVar((numberOfPeriods, numberOfDepots), vtype=GRB.CONTINUOUS, lb=0.0, name="depotCapacity")

# declare objectives
objective1, objective2, objective3 = 0,0,0

for t in range(1, numberOfPeriods):

    # Penalty Costs
    for l in range(numberOfClients):
        for p in range(numberOfProducts):
            objective1 = objective1 + penalty[p] * backDemand[t, p, l]

    #  Buying raw materials
    for m in range(numberOfRawM):
        for p in range(numberOfProducts):
            for j in range(numberOfPlants):
                for r in range(numberOfRoutes):
                     objective1 = objective1 + rawMaterialCosts[t, m] * billOfMaterials[r, m, p] * production[t, p, j,r]

    #  Production Costs and Emissions
    for p in range(numberOfProducts):
        for j in range(numberOfPlants):
            for r in range(numberOfRoutes):
                objective1 = objective1 + productionCost[r, p, j] * production[t, p, j,r]
                objective2 = objective2 + productionEmissions[r] * production[t, p, j,r]

    #  Maintaining facilities Costs
    for j in range(numberOfPlants):
        for r in range(numberOfRoutes):
            objective1 = objective1 + openPlants[t, j, r] * openPlantCosts[j, r]

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
           objective1 += (capVarPlantsUp[t,j,r]  - capVarPlantsLo[t,j,r])* EstPlantCosts[r]

    for k in range(numberOfDepots):
        objective1 += (capVarDepotsUp[t,k] - capVarDepotsLo[t,k])* EstDepotCosts

    #  IVS
    for j in range(numberOfPlants):
        for r in range(numberOfRoutes):
            objective3 = objective3 + production[t, :, j, r].sum() * ivsPlant[j]

    for k in range(numberOfDepots):
        objective3 = objective3 + shippedProductToDepots[t, :, :, :, k].sum() * ivsDepot[k]

# Establishing Facilities costs
for j in range(numberOfPlants):
    for r in range(numberOfRoutes):
        objective1 = objective1 + establishedPlants[j,r] * plantMinCapacity[r] * EstPlantCosts[r]

for k in range(numberOfDepots):
    objective1 = objective1 + establishedDepots[k] * depotMinCapacity * EstDepotCosts

# Add constraints

for p in range(numberOfProducts):
    for l in range(numberOfClients):
        # 0 backorder at start of period 1
        model.addConstr(backDemand[0, p, l] == 0, name="R01" + str(p) + str(l))

for t in range(1, numberOfPeriods):
    for l in range(numberOfClients):
        for p in range(numberOfProducts):
            # demand flow
            model.addConstr(
                shippedProductToClient[t, :, p, :, l].sum() + backDemand[t, p, l] == clientDemand[
                    t, l, p] + backDemand[t - 1, p, l], name="R02" + str(t) + str(l) + str(p))


for j in range(numberOfPlants):
    for r in range(numberOfRoutes):
        # capacity at start of first period
        model.addConstr(
            plantCapacity[0, j, r] == plantMinCapacity[r],
            name="R03" + str(j) + str(r)
        )

        for t in range(1, numberOfPeriods):

            #  capacity balance in plants
            model.addConstr(
            plantCapacity[t,j,r] == plantCapacity[t-1,j,r] + capVarPlantsUp[t,j,r] - capVarPlantsLo[t,j,r], name = "R04" + str(t) + str(j) + str(r)
            )

            # capacity limits
            model.addConstr(
            plantCapacity[t, j, r] <= plantMaxCapacity[r], name = "R05" + str(t) + str(j) + str(r)
                    )
            model.addConstr(
                plantCapacity[t, j, r] >= plantMinCapacity[r], name="R06" + str(t) + str(j) + str(r)
            )

            # limit production by capacity
            model.addConstr(production[t, :, j, r].sum() <= plantCapacity[t,j, r],
                        name="R07" + str(t) + str(j) + str(r))

for j in range(numberOfPlants):
    # establish plant
    model.addConstr(establishedPlants[j, :].sum() <= 1, name="R08" + str(j))
    for r in range(numberOfRoutes):
        for t in range(1, numberOfPeriods):
            # open plants
            model.addConstr(openPlants[t, j, r] <= establishedPlants[j, r], name="R09" + str(j) + str(r) + str(t))

for t in range(1, numberOfPeriods):
    for p in range(numberOfProducts):
        for j in range(numberOfPlants):
            for r in range(numberOfRoutes):
                # no production in closed plant
                model.addConstr(production[t, p, j, r] <= openPlants[t, j, r] * GRB.INFINITY,
                            name="R10" + str(t) + str(p) + str(j) + str(r))

    for j in range(numberOfPlants):
        for p in range(numberOfProducts):
            # products flow in plant
            model.addConstr(
                shippedProductToDepots[t, :, p, j, :].sum() == production[t, p, j, :].sum(),
                name="R11" + str(t) + str(j) + str(p))

    for k in range(numberOfDepots):

        # depot capacity
        model.addConstr(shippedProductToDepots[t, :, :, :, k].sum() <= depotCapacity[t,k],
                           name="R12" + str(t) + str(k))

        #capacity limits
        model.addConstr(
            depotCapacity[t, k] <= depotMaxCapacity,
            name="R13" + str(t) + str(k)
        )
        model.addConstr(
            depotCapacity[t, k] >= depotMinCapacity,
            name="R14" + str(t) + str(k)
        )

        # capacity balance
        model.addConstr(
            depotCapacity[t, k] == depotCapacity[t - 1, k] + capVarDepotsUp[t, k] - capVarDepotsLo[t, k],
            name="R15" + str(t) + str(k)
        )

        # depot can only open if it is established
        model.addConstr(openDepots[t, k] <= establishedDepots[k], name="R16" + str(t) + str(k))

        for p in range(numberOfProducts):
            # product flow to depot
            model.addConstr(shippedProductToDepots[t, :, p, :, k].sum() ==
                shippedProductToClient[t, :, p, k, :].sum(), name="R17" + str(t) + str(k) + str(p))

            # depot will only receive products if it is open
            model.addConstr(
                openDepots[t, k] * GRB.INFINITY - shippedProductToDepots[t, :, p, :, k].sum() >= 0,
                name="R18" + str(t) + str(k) + str(p))

for k in range(numberOfDepots):
    model.addConstr(
        depotCapacity[0, k] == depotMinCapacity,
        name="R19" + str(k)
    )

# objective restrictions
model.addConstr(objective2 <= 10, name = 'Env')
model.addConstr(objective3 >= 100, name = 'Social')

# Set objective (1 economic, 2 environmental, 3 social)
print(f'Total reading time: {round(time() - strTime, 2)} seconds')
model.setObjective(objective1, GRB.MINIMIZE)

# Optimize model
model.optimize()

# Print results
print('Resultado Final: %g' % model.objVal)
print(f'Total time: {round(time() - strTime, 2)} seconds')
model.write("outG1_MinF1.sol")
print(objective2.getValue(), "env")
print(objective3.getValue(), 'soc')


