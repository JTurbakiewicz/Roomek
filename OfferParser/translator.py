
def translate(word, case):
    for line in glossary:
        if word in line:
            if case == 'E':
                return line[0]
            elif case == 'M':
                return line[1]
            elif case == 'D':
                return line[2]
            elif case == 'C':
                return line[3]
            elif case == 'B':
                return line[4]
            elif case == 'N':
                return line[5]
            elif case == 'S':
                return line[6]
            elif case == 'W':
                return line[7]
            elif case == 'Q':
                return line[8]

