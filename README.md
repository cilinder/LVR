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
In the SATsolver_optimized.py file (everything works the same as the basic version)
Implemented the 2WL iterative algorithm. It removes the need to copy the array for every recursive call by making the backtracking not have to change the sentence, you only need to remove the last choice of unassigned literal.
In practice, it appears to work correctly as implemented and it is faster on some test cases but slower on ones with more variables (i.e. with >= 100 variables it actually performs worse than the basic recursive implementation). Why this is so, I have no idea, as it was a pain to get it to work in the first place. Perhaps a heuristic for choosing variables or random restarts would help.
