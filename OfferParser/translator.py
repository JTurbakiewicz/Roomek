
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
        ["block", "blok", "bloku", "blokowi", "blok", "blokiem", "bloku", "bloku", "blok"],
        ["apartment", "mieszkanie", "mieszkania", "mieszkaniu", "mieszkanie", "mieszkaniem", "mieszkaniu", "mieszkanie", "apartament"],
        ["", "", "", "", "", "", "", "", "kamienica"],
        # offer type:
        ["buy", "sprzedaż", "sprzedaży", "sprzedaży", "sprzedaż", "sprzedażą", "sprzedaży", "sprzedaż", "sprzedaz"],    # było 'sale'
        ["rent", "wynajem", "wynajmu", "wynajmowi", "wynajem", "wynajmem", "wynajmie", "wynajmie", "wynajem"],
        ["offering", "oferuję", "", "", "", "", "", "", "oferuję"],
        ["looking for", "szukam", "", "", "", "", "", "", "szukam"],
        ["", "", "", "", "", "", "", "", "kupno"],
        ["other", "", "", "", "", "", "", "", "pozostałe"],
        ["tenement house", "kamienica", "kamienicy", "kamienicy", "kamienicę", "kamienicą", "kamienicy", "kamienico", "kamienica"],
        ["apartment building", "apartamentowiec", "apartamentowca", "apartamentowcowi", "apartamentowiec", "apartamentowcem", "apartamentowcu", "apartamentowcu", "apartamentowiec"],
        ["secondary", "", "", "", "", "", "", "", "wtórny"],
        ["primary", "", "", "", "", "", "", "", "pierwotny"],
        ["private", "osoba prywatna", "osoby prywatnej", "osobie prywatnej", "osobę prywatną", "osobą prywatną", "osobie prywatnej", "osobo prywatna", "osoby prywatnej"],
        ["agent / developer", "biuro / deweloper", "", "", "", "", "", "", "biuro / deweloper"],
        ["reinforced concrete", "", "", "", "", "", "", "", "żelbet"],
        ["plattenbau", "", "", "", "", "", "", "", "wielka płyta"],
        ["silicate", "", "", "", "", "", "", "", "silikat"],
        ["blocks", "", "", "", "", "", "", "", "pustak"],
        ["other", "", "", "", "", "", "", "", "inne"],
        ["brick", "", "", "", "", "", "", "", "cegła"],
        ["concrete", "", "", "", "", "", "", "", "beton"],
        ["plastic", "", "", "", "", "", "", "", "plastikowe"],
        ["wood", "", "", "", "", "", "", "", "drewniane"],
        ["aluminium", "", "", "", "", "", "", "", "aluminiowe"],
        ["tiled stove", "", "", "", "", "", "", "", "piece kaflowe"],
        ["urban", "", "", "", "", "", "", "", "miejskie"],
        ["gas", "", "", "", "", "", "", "", "gazowe"],
        ["electric", "", "", "", "", "", "", "", "elektryczne"],
        ["ready", "", "", "", "", "", "", "", "do zamieszkania"],
        ["to finish", "", "", "", "", "", "", "", "do wykończenia"],
        ["to refurbish", "", "", "", "", "", "", "", "do remontu"],
        ["cooperative ownership", "", "", "", "", "", "", "", "spółdzielcze własnościowe"],
        ["cooperative ownership with book", "", "", "", "", "", "", "", "spółdzielcze wł. z KW"],
        ["full ownership", "", "", "", "", "", "", "", "pełna własność"],
        ["yes", "", "", "", "", "", "", "", "tak"],
        ["three-person", "", "", "", "", "", "", "", "trzyosobowy i więcej"],
        ["one-person", "", "", "", "", "", "", "", "jednoosobowy"],
        ["two-person", "", "", "", "", "", "", "", "dwuosobowy"],
        ["students", "", "", "", "", "", "", "", "studenci"],
        ["working people", "", "", "", "", "", "", "", "osoby pracujące"],
        ["men", "", "", "", "", "", "", "", "mężczyźni"],
        ["women", "", "", "", "", "", "", "", "kobiety"],
    ]


def translate(word, case = 'E'):
    for line in glossary:
        if word.lower() in line:
            if case == 'E':
                return line[0]
                break
            elif case == 'M':
                return line[1]
                break
            elif case == 'D':
                return line[2]
                break
            elif case == 'C':
                return line[3]
                break
            elif case == 'B':
                return line[4]
                break
            elif case == 'N':
                return line[5]
                break
            elif case == 'S':
                return line[6]
                break
            elif case == 'W':
                return line[7]
                break
            elif case == 'Q':
                return line[8]
                break
