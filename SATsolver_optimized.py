import sys
import copy
import time
import validate


class Variable:
    def __init__(self, name, val, watchlist):
        self.name = name
        self.val = val
        self.watchlist = watchlist
        self.assigned = False

def display_sentence(sentence):
    print('[', end ="")
    firstSentence = True
    for clause in sentence:
        if not firstSentence:
            print(' & ', end ="")
        else:
            firstSentence = False
        print('(', end ="")
        first = True
        for var in clause:
            if not first:
                print(' v ', end ="")
            else:
                first = False
            if var < 0:
                print('┐', end ="")
            print('x'+str(abs(var)), end ="")
        print(')', end ="")
    print(']')

# not optimized
def simplify_sentence(sentence, unitClause):
    literal = unitClause[0]
    simplified = []
    for clause in sentence:
        if literal in clause:
            continue
        if -literal in clause:
            clause.remove(-literal)
            simplified.append(clause)
        else:
            simplified.append(clause)
    return simplified

def find_units_and_simplify(sentence, val):
    for clause in sentence:
        if len(clause) == 1:
            sentence = simplify_sentence(sentence, clause)
            val.append(clause[0])
            sentence, val = find_units_and_simplify(sentence, val)
            break

    return sentence, val

def backtrack(decision_stack, decision_level, propagation_queue):
    decision_stack.pop()
    propagation_queue.clear()
    return decision_level-1

def has_unassigned_variables(assignments, nbvars):
    return len(assignments) < nbvars


def eliminate_redundant_clauses(sentence):

    newSentence = []
    for clause in sentence:
        addClause = True
        for var in clause:
            if -var in clause:
                addClause = False
                break
        if addClause:
            newSentence.append(clause)
    return newSentence

def parse_dimacs(lines):
    sentence = []
    variables = []

    for line in lines:
        if line[0] == 'c':
            continue
        elif line[0] == 'p':
            nums = [int(s) for s in line.split() if s.isdigit()]
            nbvar = nums[0]
            nbclauses = nums[1]

            variables = [None] * 2*nbvar

            for i in range(nbvar):
                variables[i] = (Variable(i+1, True, []))
                variables[-i-1] = (Variable(-(i+1), False, []))


        elif line[0] == '%':
            break
        else:
            clause = []
            for t in line.split():
                try:
                    t = int(t)
                    if t == 0:
                        continue
                    val = t > 0 # if t > 0 then val = True, if t < 0 then val = False
                    for var in variables:
                        if var.name == t:
                            clause.append(var)
                except ValueError:
                    pass
            sentence.append(clause)

            clause[0].watchlist.append(clause)
            if len(clause) >= 2:
                clause[1].watchlist.append(clause)
    return (sentence, variables, nbvar, nbclauses)


def create_index(sentence, nbvar):

    index = [None] * nbvar
    for i in range(nbvar):
        index[i] = [[], []]

    for clause in sentence:
        for var in clause:
            if var > 0:
                index[var-1][0].append(clause)
            else:
                index[-var-1][1].append(clause)
    return index

# the method for deciding which variable we will try next
def pick_variable(variables):
    for var in variables:
        n = -var.name
        if n > 0:
            n -= 1
        if not var.assigned and not variables[n].assigned:
            return var
    raise RuntimeError

def create_watchlist(sentence, nbvar, nbclauses): # we assume every clause has at least 2 literals, otherwise it can be propagated already
    watchlist = [None] * nbvar
    for i in range(nbvar):
        watchlist[i] = [None] * 2
    for clause in sentence:
        if len(clause) < 2:
            raise RuntimeError
        index1 = (abs(clause[0]) + 1) / 2
        watchlist[abs(clause[0])][index1] = clause
        index2 = (abs(clause[1]) + 1) / 2
        watchlist[abs(clause[1])][index2] = clause

    return watchlist

def DPLL(sentence, variables, nbvar, nbclauses):

    decision_stack = []
    propagation_queue = []
    assignments = []
    decision_level = 0

    # first round of propagations, if there are already unit clauses
    for clause in sentence:
        if len(clause) == 1:
            clause[0].assigned = True
            assignments.append(clause[0])
            n = -clause[0].name
            if n > 0:
                n -= 1
            propagation_queue.append(variables[n])
    decision_stack.append([var for var in assignments])

    if propagate(sentence, variables, decision_stack, assignments, propagation_queue, nbclauses) == "CONFLICT":
        return "UNSAT"

    decision_stack.pop()

    while has_unassigned_variables(assignments, nbvar):  # not all variables have been assigned a value
        x = pick_variable(variables)
        n = -x.name
        if n > 0:
            n -= 1
        x.assigned = True
        propagation_queue.append(variables[n])  # add -x to the list of variables that cannot be watched
        decision_stack.append([x])
        assignments.append(x)

        decision_level += 1

        while propagate(sentence, variables, decision_stack, assignments, propagation_queue, nbclauses) == "CONFLICT":
            if decision_level == 0:
                return (False, None)
            decision_level -= 1
            propagation_queue.clear()
            #current = decision_stack[decision_level]
            current = decision_stack[-1]
            for var in current:
                var.assigned = False
                assignments.remove(var)
            decision_stack.pop()
            x = current[0]

            n = -x.name
            if n > 0:
                n -= 1
            not_x = variables[n]
            x.assigned = False
            not_x.assigned = True
            if decision_level > 0:
                decision_stack[-1].append(not_x)
            else:
                decision_stack.append([not_x])
                decision_level += 1
            assignments.append(not_x)
            propagation_queue.append(x)
    return (True, assignments)


def propagate(sentence, variables, decision_stack, assignments, prop_queue, nbclauses):

    while prop_queue:
        x = prop_queue.pop()
        remove_list = []

        # find all clauses watched by x
        for watched_clause in x.watchlist:
            x_slot = None
            if len(watched_clause) == 1:
                x_slot = 0
                y = x
            elif watched_clause[0] == x:
                x_slot = 0
                y = watched_clause[1]
            else:
                x_slot = 1
                y = watched_clause[0]
            if y in assignments:
                continue
            # check if there is a different literal in the clause we can watch
            found_another = False
            for i in range(2, len(watched_clause)):
                var = watched_clause[i]
                n = -var.name
                if n > 0:
                    n -= 1
                other = variables[n]
                if var.assigned == True or other.assigned == False:
                    # other will be the new watched literal instead of x
                    watched_clause[x_slot] = var
                    watched_clause[i] = x
                    remove_list.append(watched_clause)
                    #x.watchlist.remove(watched_clause)
                    var.watchlist.append(watched_clause)
                    found_another = True
                    break
            if not found_another:
                n = -y.name
                if n > 0:
                    n -= 1
                if variables[n].assigned:
                    return "CONFLICT"
                else:
                    y.assigned = True
                    decision_stack[-1].append(y)
                    assignments.append(y)
                    prop_queue.append(variables[n])

        for clause in remove_list:
            x.watchlist.remove(clause)

    return "DONE"


if __name__ == "__main__":

    time1 = time.time()

    for i in range(1):
        filename='.\\tests\\uf20-0' + str(8+1) + '.cnf'
        #filename = 'sudoku_hard.txt'

        file = open(filename, "r")
        lines = file.readlines()

        sentence, variables, nbvar, nbclauses = parse_dimacs(lines)
        sentence.sort(key=len)

        nbclauses = len(sentence)

        assignments = []

        sat, assignments = DPLL(sentence, variables, nbvar, nbclauses)
        val = [var.name for var in assignments]
        if not sat:
            print("UNSAT")
            continue

        validation_sentence = [[var.name for var in clause] for clause in sentence]

        validate.validate(validation_sentence, val)

    time2 = time.time()
    print('the function took {:.3f} s'.format((time2 - time1)))