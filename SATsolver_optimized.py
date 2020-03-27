import sys
import copy
import time
import validate


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

def has_unassigned_variables(assignments):

    for i in assignments:
        if i is None:
            return True
    return False

def DPLL(sentence, nbvar, nbclauses):
    variables = [i + 1 for i in range(nbvar)]

    assignments = [None] * nbvar
    decision_stack = []
    propagation_queue = []
    decision_level = 0

    watchlist = create_watchlist(sentence, nbvar, nbclauses)

    while has_unassigned_variables(assignments):  # not all variables have been assigned a value
        x = pick_variable(assignments)
        propagation_queue.append(-x)  # add -x to the list of variables that cannot be watched
        decision_stack.append([x])

        assignments[abs(x)-1] = x

        decision_level += 1
        # now propagate this decision
        while propagate(sentence, assignments, decision_stack, propagation_queue, watchlist, nbclauses) == "CONFLICT":
            if decision_level == 0:
                return (False, None)
            decision_level -= 1
            propagation_queue.clear()
            current = decision_stack[decision_level]
            decision_stack.pop()
            x = current[0]
            for i in current:
                assignments[abs(i)-1] = None

            assignments[abs(x)-1] = -x
            if decision_level > 0:
                decision_stack[-1].append(-x)
            else:
                decision_stack.append([-x])
            propagation_queue.append(x)

    return (True, assignments)

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

    for line in lines:
        if line[0] == 'c':
            continue
        elif line[0] == 'p':
            nums = [int(s) for s in line.split() if s.isdigit()]
            nbvar = nums[0]
            nbclauses = nums[1]
        elif line[0] == '%':
            break
        else:
            clause = []
            for t in line.split():
                try:
                    clause.append(int(t))
                except ValueError:
                    pass
            sentence.append(clause[:-1])
    return (sentence, nbvar, nbclauses)


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
def pick_variable(assignments):
    for i, var in enumerate(assignments):
        if var is None:
            return i+1

def create_watchlist(sentence, nbvar, nbclauses): # we assume every clause has at least 2 literals, otherwise it can be propagated already
    watchlist = [None] * nbclauses
    for i in range(nbclauses):
        watchlist[i] = [sentence[i][0]]
        watchlist[i].append(sentence[i][1])
    return watchlist

def propagate(sentence, assignments, decision_stack, prop_queue, watchlist, nbclauses):

    inside_assignments = []
    while prop_queue:
        x = prop_queue.pop()
        for i in range(nbclauses):
            for j in [0,1]:
                if x == watchlist[i][j]:
                    y = watchlist[i][1-j]
                    if y in assignments:
                        break
                    found_another = False
                    for var in sentence[i]:
                        if var != x and var != y and -var not in assignments:
                            watchlist[i][j] = var
                            found_another = True
                    if not found_another:
                        if -y in assignments:
                            for k in inside_assignments:
                                assignments[abs(k)-1] = None
                            return "CONFLICT"
                        else:
                            assignments[abs(y)-1] = y
                            inside_assignments.append(y)
                            prop_queue.append(-y)

    return "DONE"

if __name__ == "__main__":

    time1 = time.time()

    for i in range(100):
        filename='.\\tests\\uf20-0' + str(i+1) + '.cnf'

        file = open(filename, "r")
        lines = file.readlines()

        sentence, nbvar, nbclauses = parse_dimacs(lines)
        sentence.sort(key=len)
        sentence = eliminate_redundant_clauses(sentence)
        sentence, val = find_units_and_simplify(sentence, [])

        nbclauses = len(sentence)

        assignments = []

        if len(val) < nbvar:
            sat , assignments = DPLL(sentence, nbvar, nbclauses)
            if not sat:
                print("UNSAT")
                continue

        validate.validate(sentence, assignments + val)

    time2 = time.time()
    print('the function took {:.3f} s'.format((time2 - time1)))