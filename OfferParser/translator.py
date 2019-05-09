
# 0 = "E" = English
# 1 = "M" = Mianownik (kto? co?) stoi
# 2 = "D" = Dopełniacz (kogo? czego?) nie ma
# 3 = "C" = Celownik (komu? czemu?) przyglądam się
# 4 = "B" = Biernik (kogo? co?) widzę
# 5 = "N" = Narzędnik (z kim? z czym?) idę
# 6 = "S" = Miejscownik (o kim? o czym?) mówię
# 7 = "W" = Wołacz (hej? o?) zatrzymaj się
# 8 = "Q" = Z bazy danych

glossary = [
        # housing type:
        ["room", "pokój", "pokoju", "pokojowi", "pokój", "pokojem", "pokoju", "pokoju", "stancje-pokoje"],
        ["block", "", "", "", "", "", "", "", "blok"],
        ["apartment", "", "", "", "", "", "", "", "mieszkanie"],
        ["apartment", "", "", "", "", "", "", "", "apartament"],
        ["", "", "", "", "", "", "", "", "kamienica"],
        # offer type:
        ["", "", "", "", "", "", "", "", "sprzedaz"],
        ["rent", "wynajem", "wynajmu", "wynajmowi", "wynajem", "wynajmem", "wynajmie", "wynajmie", "wynajem"],
        ["", "", "", "", "", "", "", "", "kupno"]
    ]


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
