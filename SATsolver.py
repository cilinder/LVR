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

def DPLL(sentence, val):

    simplifiedSentence = copy.deepcopy(sentence)
    simplifiedSentence, val = find_units_and_simplify(simplifiedSentence, val)

    if len(simplifiedSentence) == 0:
        return (True, val)
    for clause in simplifiedSentence:
        if len(clause) == 0:
            return (False, [])

    chosenLiteral = simplifiedSentence[0][0]
    success, newVal = DPLL([[chosenLiteral]] + simplifiedSentence, val.copy())
    if success:
        return (success, newVal)
    success, newVal = DPLL([[-chosenLiteral]] + simplifiedSentence, val.copy())
    if success:
        return (success, newVal)
    else:
        return (False, [])

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
    return sentence

if __name__ == "__main__":

    filename=sys.argv[1]
    file = open(filename, "r")
    lines = file.readlines()

    sentence = parse_dimacs(lines)
    sentence.sort(key=len)
    file.close()

    sentence = eliminate_redundant_clauses(sentence)

    success, val = DPLL(sentence, [])
    if len(sys.argv) >= 3:
        outputfilename = sys.argv[2]
        outputfile = open(outputfilename, "w")
    else:
        outputfile = sys.stdout
    if success:
        #validate.validate(sentence, val)
        for x in val:
            print(x, file=outputfile, end=" ")
    else:
        print('NOSAT')
        outputfile.write('0')

    outputfile.close()
