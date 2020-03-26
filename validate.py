import sys

def validate(sentence, solution):
    solved = True
    for clause in sentence:
        sol = False
        for var in clause:
            if var in solution:
                sol = True
                break
            elif -var in solution:
                continue
            else:
                solution.append(var)
                sol = True
                break
        if sol == False:
            print("FAIL")
            print(clause)
            solved = False
            break

    if solved:
        print("SOLVED")
if __name__ == "__main__":

    filename = sys.argv[1]
    file = open(filename, "r")
    lines = file.readlines()
    file.close()
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

    filename = sys.argv[2]
    file = open(filename, "r")
    line = file.readline()

    solution = []
    for t in line.split():
        try:
            solution.append(int(t))
        except ValueError:
            pass

    validate(sentence, solution)
