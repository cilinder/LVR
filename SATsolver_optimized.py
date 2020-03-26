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

def DPLL(sentence, index, decision_stack, assignments):

    simplifiedSentence = copy.deepcopy(sentence)
    simplifiedSentence, vals = find_units_and_simplify(simplifiedSentence, [])

    for val in vals:
        if val > 0:
            assignments[val-1] = True
        else:
            assignments[-val-1] = False

    decision_stack.append(vals)

    

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


if __name__ == "__main__":

    time1 = time.time()

    for i in range(1):
        filename='.\\tests\\CBS_k3_n100_m403_b10_' + str(i+1) + '.cnf'
        filename = 'test.txt'

        file = open(filename, "r")
        lines = file.readlines()

        sentence, nbvar, nbclauses = parse_dimacs(lines)
        sentence.sort(key=len)
        sentence = eliminate_redundant_clauses(sentence)

        assignments = [None] * nbvar
        decision_stack = []

        index = create_index(sentence, nbvar)

        success, val = DPLL(sentence, index, decision_stack, assignments)
        #outputfilename = sys.argv[2]
        #outputfile = open(outputfilename, "w")
        if success:
            continue
            #print('SAT')
            #for value in val:
                #outputfile.write("%i " % value)
        else:
            print('NOSAT')
            #outputfile.write('0')

        #outputfile.close()

        #validate.validate(sentence, val)

    time2 = time.time()
    print('the function took {:.3f} s'.format((time2 - time1)))