import sys

if __name__ == "__main__":
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    file1 = open(filename1, "r")
    file2 = open(filename2, "r")
    lineS1 = file1.readline()
    lineS2 = file2.readline()

    lineS1 = lineS1.split(" ")
    lineS2 = lineS2.split(" ")

    lineS1.sort()
    lineS2.sort()

    neki = 1
    nekineki = []
    for x in lineS2:
        if x not in lineS1:
            neki = 0
            nekineki.append(x)

    if neki == 1:
        print ("kul")
    else:
        print("ni kul")
        print(nekineki)