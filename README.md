# SSCND
Datasets and results for "Optimizing the Sustainable Steel Supply Chain" manuscript

The files available in this repository are divided into three categories, data, results and algorithms.

# DATA

In this folder, the datasets we constructed and used in the paper is presented. The I1, I2 and I3 folders contain data from the first through third instances, respectively. The tradeoff analysis folder contain data used for analyzing the results. All data is available in .csv and files are organized as follows:

•	bom : Bill Of Materials
•	demand: product demand per period;
•	depotMaxCapacity: Maximum capacity for DCs;
•	depotMinCapacity: Minimum capacity for DCs;
•	estDepot: costs for establishing depots per ton of capacity;
•	estPlant: cost for establishing plants per ton of capacity;
•	ivsDepot: SVI for depots;
•	ivsPlants: SVI for plants;
•	jToK: distances from plants to DCs per transport mode;
•	kToL: distances from DCs to costumers per transport mode;
•	openDepot: costs for maintaining depots;
•	openPlant: costs for maintain plants;
•	penalty: penalties applied in case of backordered demand, per ton of product;
•	plantMaxCapacity: Maximum capacity for plants;
•	plantMinCapacity: Minimum capacity for plants;
•	productionCost: costs for production per product and route;
•	production emission: CO2 emissions in production per ton of crude steel;
•	rawMaterialCost: costs of raw materials;
•	sets: total number of items in each set;
•	transportCosts: costs of transport;
•	transportEmission: CO2 emissions in transport;

# RESULTS 

The results folder contains the output for the GA in each instance and each tradeoff analysis. There are three files for each output. The first one contains all objective functions (OF) values for the 100 individuals in the final population (obj). The second file contains all individuals in the final population (pop) and the third file contains the decoded values for the output variables (var). The file names are organized as the example below:

Output_instance_seed_type

Therefore, a file for the objective values for the instance I2, seed 11, will be named: 

Output_I2_11_obj

The first four lines of the obj type files display the following:
•	Line 1: Best objective values found for the first generations in each O.F (order: economical, environmental, social).
•	Line 2: number of function calls and total resolution time.
•	Line 3: Best objective values found at the end of the run in each O.F (order: economical, environmental, social).
•	Line 4: total number of generations.

The rest of the lines contain the O.F values for each of the 100 individuals in the final population.

The order of the variables available in the var type files is: 
Backordered demand, shipped products to DCs, shipped products to clients, production, established plants, established DCs, open plants, open DCs, positive capacity variation for plants, negative capacity variation for plants, positive capacity variation for DCs and negative capacity variation for DCs.

# ALGORITHMS

This folder contains the python files used to run the GA and the epsilon-constraint methods. For the GA, the principal file is called main.py, and is responsible for calling each of the other files. For the epsilon-constraint, the model build using gurobipy for solving with Gurobi can be found in the model.py file.
