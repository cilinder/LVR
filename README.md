# SAT solver

SAT solver takes SAT problem defined in conjunctive normal form and attempts to find some satisfying valuation. If such valuation is found it is returned, otherwise solver returns a single value of 0.

## Running the solver
Solver can be ran as: `python SATsolver.py <input filename> [output filename]`

SAT solver takes input file that contains CNF formula (in Dimacs format) of SAT problem to solve.
Solution can be printed to STDOUT (default) or written to file.

Example calls:
+ CNF formula is stored in file '*my_cnf.txt*':
`python SATsolver.py my_cnf.txt`

+ CNF formula is stored in '*my_cnf.txt*', solution should be written to '*solution.txt*':
`python SATsolver.py my_cnf.txt solution.txt`

## Optimization attempt
