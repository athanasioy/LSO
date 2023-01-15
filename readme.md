# Large Scale Optimazation, AUEB
## Vehicle Route Problem
### Semester Assignment
_Antonis Athanasioy_ , _Stavroula Atzami_, _Panagiota Gkourioti_,  _Thaleia Koletsi_

The following code solves a Vehicle Route Problem using a fixed number of vehicles and serves 200 customers.
The objective of the problem is to minimize the time that the last customer is served under our problem.

For fully reproducible results, run the main.py as is. The other files contain objects that were used during experimentation and are not part of the final solution.


### Main Files Explaination

#### config.ini

Contains configation data such as number of customers, vehicle capacity etc.

#### main.py
Entry point of the code. Initialize nodes, vehicles and creates the necessary objects for the problem.

#### map_objects (directory)

Holds objects such as the Node, Vehicle, Route and MapManager

#### solver_objects (directory)

Holds objects that are used to calculate solutions, including the Solution Object

**algorithm.py** contains the greedy algorithms that generate initial solutions

**optimizer.py** contains the Move Types that generate a solution Neighborhood

**combiners.py** contains objects that use Optimizers to generate better solutions
here VND, VND-GLS etc. are included

**solution.py** contains the solution object and helper methods.

**legacy.py** is basically junk code

#### Other files

the other files contain either superclasses such as OptimizerABC.py or helper dataclasses such as move.py

