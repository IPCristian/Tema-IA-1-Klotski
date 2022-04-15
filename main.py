import copy
import os
import sys
import time


# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:
    def __init__(self, info, parinte, cost=0, h=0, piesa='#', miscare=''):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h
        self.piesa = piesa
        self.miscare = miscare

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for i, nod in enumerate(l):
            if 0 < i < len(l) - 1:
                output.write("Mutam piesa {} in {}\n".format(nod.piesa, nod.miscare))
            elif i == len(l) - 1:
                output.write("Mutam piesa * in {}\n".format(nod.miscare))
            output.write(str(i+1) + ")\n")
            for j in range(1, len(nod.info) - 1):
                for k in range(1, len(nod.info[0]) - 1):
                    output.write(str(nod.info[j][k]) + " ")
                output.write("\n")
            output.write("\n")
        if afisCost:
            output.write("Cost: " + str(self.g) + "\n")
        if afisLung:
            output.write("Lungime: " + str(len(l)) + "\n")

        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return sir

    def __str__(self):
        sir = ""
        for linie in self.info:
            sir += " ".join([str(elem) for elem in linie]) + "\n"
        sir += "\n"
        return sir


class Graph:  # graful problemei
    def __init__(self, nume_fisier):
        f = open(nume_fisier, "r")
        sirFisier = f.read()
        try:
            listaLinii = sirFisier.strip().split("\n")
            self.start = []
            self.start.append([str(x) for x in ('.' * (len(listaLinii[0]) + 2))])  # Bordam puzzle-ul intr-un strat de
            for linie in listaLinii:  # spatii libere, astfel ne asiguram
                linie = '.' + linie + '.'  # ca piesa * poate iesi cu succes
                self.start.append([str(x) for x in linie])
            self.start.append([str(x) for x in ('.' * (len(listaLinii[0]) + 2))])
            # for linie in self.start:
            #     print(linie)
            self.NrLinii = len(self.start)
            self.NrCol = len(self.start[0])
            self.Iesiri = []  # Tupluri de coordonate ale '.' din inputul original
            for i in range(1, self.NrLinii - 1):
                if self.start[i][1] != '#':  # Prima coloana
                    self.Iesiri.append((i, 1))
                if self.start[i][self.NrCol - 2] != '#':  # Ultima coloana
                    self.Iesiri.append((i, self.NrCol - 2))

            for i in range(2, self.NrCol - 1):
                if self.start[1][i] != '#':  # Prima linie mai putin colturile luate deja
                    self.Iesiri.append((1, i))
                if self.start[self.NrLinii - 2][i] != '#':  # Ultima linie mai putin colturile luate deja
                    self.Iesiri.append((self.NrLinii - 2, i))

            # print("Coordonate iesiri: " + str(self.Iesiri))
        except:
            output.write("Eroare la parsare!\n")
            sys.exit(0)  # iese din program

    def testeaza_scop(self, nodCurent):
        # for linie in nodCurent.info:
        #     print(linie)
        # print("\n")
        for linie in nodCurent.info:
            if '*' in linie:
                return False
        return True

    def nuAreSolutii(self, infoNod):
        if len(self.Iesiri) == 0:
            raise ValueError("Inputul nu are solutii. Nu exista iesiri")

        for linie in infoNod:
            if (linie.count('*') > len(self.Iesiri)) and (
                    self.Iesiri[0][0] == 1 or self.Iesiri[0][0] == self.NrLinii - 2):
                raise ValueError("Inputul nu are solutii. Iesirea este mai mica decat piesa")

        coloane = []
        for i in range(0, len(infoNod[0])):
            coloane.append(0)

        for i in range(1, len(infoNod) - 1):
            for j in range(1, len(infoNod[0]) - 1):
                if infoNod[i][j] == '*':
                    coloane[j - 1] += 1

        for i in coloane:
            if i > len(self.Iesiri) and (self.Iesiri[0][1] == 1 or self.Iesiri[0][1] == self.NrCol - 2):
                raise ValueError("Inputul nu are solutii. Iesirea este mai mica decat piesa")

    def mutare(self, infoNou, caracter_piesa, lin_gol, col_gol, lin_prima_mutare, col_prima_mutare):

        cost_mutare = 1
        coordonate_vizitate = []

        coada = [(lin_prima_mutare, col_prima_mutare)]
        while len(coada):

            lin, col = coada.pop(0)
            coordonate_mutare = (lin + (lin_gol - lin_prima_mutare), col + (col_gol - col_prima_mutare))
            coordonate_vizitate.append((lin, col))

            if infoNou[coordonate_mutare[0]][coordonate_mutare[1]] != '.':  # Daca o bucata nu poate fi mutata
                return False, -1  # atunci intreaga piesa nu poate fi mutata

            directii = [(lin, col - 1), (lin, col + 1), (lin - 1, col), (lin + 1, col)]
            for directie in directii:  # Cautam si restul de bucati din piesa
                if 1 <= directie[0] < self.NrLinii - 1:
                    if 1 <= directie[1] < self.NrCol - 1:
                        if infoNou[directie[0]][directie[1]] == caracter_piesa and (
                                directie[0], directie[1]) not in coordonate_vizitate:
                            cost_mutare += 1  # Adaugam 1 cost pentru fiecare bucata ce trebuie mutata
                            coada.append((directie[0], directie[1]))

            if 1 <= coordonate_mutare[0] < self.NrLinii - 1 and 1 <= coordonate_mutare[1] < self.NrCol - 1:
                infoNou[coordonate_mutare[0]][coordonate_mutare[1]] = caracter_piesa
                infoNou[lin][col] = '.'
            elif caracter_piesa == '*':  # Daca piesa care dorim sa o mutam este piesa speciala, aceasta este
                infoNou[lin][col] = '.'  # singura care poate fi mutata pe marginea puzzle-ului. La mutarea
                # ei pe margine, aceasta este inlocuita cu un spatiu liber

        if caracter_piesa == '*':  # Daca piesa este speciala, mereu costul va fi 1, indiferent de dimensiune
            cost_mutare = 1

        return True, cost_mutare

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []

        for lin in range(self.NrLinii):
            for col in range(self.NrCol):
                if nodCurent.info[lin][col] == '.':  # Cautam un spatiu gol
                    directii = [(lin, col - 1), (lin, col + 1), (lin - 1, col), (lin + 1, col)]

                    """ Ne uitam in jurul sau ce piese am putea muta in locul
                    sau. Daca inca suntem inauntrul puzzle-ului, iar piesa
                    gasita nu reprezinta un perete sau un spatiu gol,
                    incercam sa o mutam. """

                    for directie in directii:
                        if 0 <= directie[0] < self.NrLinii:
                            if 0 <= directie[1] < self.NrCol:
                                if nodCurent.info[directie[0]][directie[1]] not in ['.', '#']:
                                    infoCrt = copy.deepcopy(nodCurent.info)
                                    mutare_valida, cost_mutare = self.mutare(infoCrt, infoCrt[directie[0]][directie[1]],
                                                                             lin, col, directie[0], directie[1])

                                    if nodCurent.contineInDrum(infoCrt):  # Daca am mai parcurs aceasta mutare,
                                        mutare_valida = False  # atunci trecem peste

                                    for nod in listaSuccesori:  # Daca deja am gasit aceasta mutare si
                                        if nod.info == infoCrt:  # urmeaza sa o parcurgem, nu o mai adaugam
                                            mutare_valida = False  # la lista de succesori posibili

                                    if mutare_valida:
                                        directie_mutare = (lin - directie[0], col - directie[1])
                                        if directie_mutare[0] == 0 and directie_mutare[1] == -1:
                                            directie_mutare_string = "stanga"
                                        elif directie_mutare[0] == 0 and directie_mutare[1] == 1:
                                            directie_mutare_string = "dreapta"
                                        elif directie_mutare[0] == -1 and directie_mutare[1] == 0:
                                            directie_mutare_string = "sus"
                                        else:
                                            directie_mutare_string = "jos"

                                        listaSuccesori.append(
                                            NodParcurgere(infoCrt, nodCurent, nodCurent.g + cost_mutare,
                                                          self.calculeaza_h(infoCrt, tip_euristica),
                                                          infoCrt[lin][col], directie_mutare_string))
        return listaSuccesori

    def calculeaza_h(self, infoNod, tip_euristica="euristica banala"):
        if self.testeaza_scop(NodParcurgere(infoNod, None)):
            return 0
        if tip_euristica == "euristica banala":
            return 1
        elif tip_euristica == "euristica admisibila 1":
            h = 0
            coordonate_star = []  # Cautam coordonatele tutoror '*' din input
            for i in range(len(infoNod)):
                for j in range(len(infoNod[0])):
                    if infoNod[i][j] == '*':
                        coordonate_star.append((i, j))

            for stea in coordonate_star:  # Facem distanta Manhattan de la fiecare '*' la cea mai apropiata iesire
                min_dist = []
                for punct in self.Iesiri:
                    min_dist.append(abs(stea[0] - punct[0]) + abs(stea[1] - punct[1]))
                h += min(min_dist)  # Facem suma minimelor
            return h
        elif tip_euristica == "euristica neadmisibila":
            h = 0
            for i in range(len(infoNod)):
                for j in range(len(infoNod[0])):
                    if infoNod[i][j] == '*':
                        h += (self.NrLinii * self.NrCol)
            return h

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return sir


def breadth_first(gr, nrSolutiiCautate):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None)]
    nr_nod_total = 0
    nr_nod_max = 0
    nr_nod_temp = 0
    while len(c) > 0:
        # print("Coada actuala: " + str(c))
        # input()
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            output.write(str(time.time() - t1) + " secunde\n")
            output.write("Solutie:\n")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            output.write("Numar noduri totale in memorie: " + str(nr_nod_total) + "\n")
            if nr_nod_max < nr_nod_temp:
                nr_nod_max = nr_nod_temp
            nr_nod_temp = 0
            output.write("\n----------------\n\n")
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                output.write("Numar noduri maxime in memorie: " + str(nr_nod_max) + "\n")
                return

        if time.time() - t1 > timeout:
            output.write("Trecut  de timp limita\n")
            return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        nr_nod_temp += len(lSuccesori)
        nr_nod_total += len(lSuccesori)
        c.extend(lSuccesori)


def depth_first(gr, nrSolutiiCautate=1):
    try:
        df(NodParcurgere(gr.start, None), nrSolutiiCautate, 0, 0, 0)
    except RecursionError as re:
        output.write("Algoritmul de Depth First a ajuns la Recursie maxima: {}\n".format(re.args[0]))


def df(nodCurent, nrSolutiiCautate, nr_nod_total, nr_nod_temp, nr_nod_max):
    if nrSolutiiCautate <= 0:
        return nrSolutiiCautate
    if gr.testeaza_scop(nodCurent):
        output.write(str(time.time() - t1) + " secunde\n")
        output.write("Solutie: \n")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        output.write("Numar noduri totale in memorie: " + str(nr_nod_total) + "\n")
        if nr_nod_temp > nr_nod_max:
            nr_nod_max = nr_nod_temp
        nr_nod_temp = 0
        output.write("\n----------------\n\n")
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            output.write("Numar noduri maxime in memorie: " + str(nr_nod_max) + "\n")
            return nrSolutiiCautate
    if time.time() - t1 > timeout:
        output.write("Trecut  de timp limita\n")
        return
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    nr_nod_total += len(lSuccesori)
    nr_nod_temp += len(lSuccesori)
    for sc in lSuccesori:
        if nrSolutiiCautate != 0:
            nrSolutiiCautate = df(sc, nrSolutiiCautate, nr_nod_total, nr_nod_temp, nr_nod_max)
    return nrSolutiiCautate


def dfi(nodCurent, adancime, nrSolutiiCautate, nr_nod_total, nr_nod_temp, nr_nod_max):
    # print(str(nodCurent) + "\n")
    if adancime == 1 and gr.testeaza_scop(nodCurent):
        output.write(str(time.time() - t1) + " secunde\n")
        output.write("Solutie: \n")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        output.write("Numar noduri totale in memorie: " + str(nr_nod_total) + "\n")
        if nr_nod_temp > nr_nod_max:
            nr_nod_max = nr_nod_temp
        nr_nod_temp = 0
        output.write("\n----------------\n\n")
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            output.write("Numar noduri maxime in memorie: " + str(nr_nod_max) + "\n")
            return nrSolutiiCautate
    if adancime > 1:
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        nr_nod_temp += len(lSuccesori)
        nr_nod_total += len(lSuccesori)
        for sc in lSuccesori:
            if nrSolutiiCautate != 0:
                nrSolutiiCautate = dfi(sc, adancime - 1, nrSolutiiCautate, nr_nod_total, nr_nod_temp, nr_nod_max)
    return nrSolutiiCautate


def depth_first_iterativ(gr, nrSolutiiCautate=1):
    nr_nod_total = 0
    nr_nod_temp = 0
    nr_nod_max = 0
    for i in range(1, 25):
        if time.time() - t1 > timeout:
            output.write("Trecut  de timp limita\n")
            return
        if nrSolutiiCautate == 0:
            return
        output.write("**************\nAdancime maxima: " + str(i) + "\n")
        nrSolutiiCautate = dfi(NodParcurgere(gr.start, None), i, nrSolutiiCautate, nr_nod_total, nr_nod_temp,
                               nr_nod_max)


def a_star(gr, nrSolutiiCautate, tip_euristica):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]
    nr_nod_total = 0
    nr_nod_temp = 0
    nr_nod_max = 0

    while len(c) > 0:

        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            output.write(str(time.time() - t1) + " secunde\n")
            output.write("Solutie: \n")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            output.write("Numar noduri totale in memorie: " + str(nr_nod_total) + "\n")
            if nr_nod_temp > nr_nod_max:
                nr_nod_max = nr_nod_temp
            nr_nod_temp = 0
            output.write("\n----------------\n")
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                output.write("Numar noduri maxime in memorie: " + str(nr_nod_max) + "\n")
                return
        if time.time() - t1 > timeout:
            output.write("Trecut  de timp limita \n")
            return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        nr_nod_total += len(lSuccesori)
        nr_nod_temp += len(lSuccesori)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


def a_star_optimizat(gr, nrSolutiiCautate, tip_euristica):
    nr_nod_total = 0
    nr_nod_max = 0
    nr_nod_temp = 0
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    l_open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]

    # l_open contine nodurile candidate pentru expandare (este echivalentul lui c din A* varianta neoptimizata)

    # l_closed contine nodurile expandate
    l_closed = []
    while len(l_open) > 0:
        # print("Coada actuala: " + str(l_open))
        # input()
        nodCurent = l_open.pop(0)
        l_closed.append(nodCurent)
        if gr.testeaza_scop(nodCurent):
            output.write(str(time.time() - t1) + " secunde\n")
            output.write("Solutie: \n")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            output.write("Numar noduri totale in memorie: " + str(nr_nod_total) + "\n")
            if nr_nod_temp > nr_nod_max:
                nr_nod_max = nr_nod_temp
            nr_nod_temp = 0
            output.write("\n----------------\n\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                output.write("Numar noduri maxime in memorie: " + str(nr_nod_max) + "\n")
                return
        if time.time() - t1 > timeout:
            output.write("Trecut  de timp limita\n")
            return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        nr_nod_total += len(lSuccesori)
        nr_nod_temp += len(lSuccesori)
        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        l_open.remove(nodC)
                    break
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            l_closed.remove(nodC)
                        break
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                l_open.insert(i, s)
            else:
                l_open.append(s)


def ida_star(gr, nrSolutiiCautate, tip_euristica):
    nr_nod_total = 0
    nr_nod_temp = 0
    nr_nod_max = 0
    nodStart = NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))
    limita = nodStart.f
    while True:
        if time.time() - t1 > timeout:
            output.write("Trecut  de timp limita\n")
            return
        output.write("Limita de pornire: " + str(limita) + "\n")
        nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, tip_euristica,
                                                  nr_nod_total, nr_nod_temp, nr_nod_max)
        if rez == "gata":
            break
        if rez == float('inf'):
            output.write("Nu mai exista solutii!\n")
            break
        limita = rez
        output.write(">>> Limita noua: " + str(limita) + "\n")
        # input()


def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate, tip_euristica, nr_nod_total, nr_nod_temp, nr_nod_max):
    # print("A ajuns la: ")
    # for i in range(1, len(nodCurent.info) - 1):
    #     for j in range(1, len(nodCurent.info[0]) - 1):
    #         print(str(nodCurent.info[i][j]) + " ", end="", sep=" ")
    #     print()
    # print("\n")
    if nodCurent.f > limita:
        return nrSolutiiCautate, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f <= limita:
        output.write(str(time.time() - t1) + " secunde\n")
        output.write("Solutie: \n")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        output.write("Numar noduri totale in memorie: " + str(nr_nod_total) + "\n")
        if nr_nod_temp > nr_nod_max:
            nr_nod_max = nr_nod_temp
        nr_nod_temp = 0
        output.write(str(limita))
        output.write("\n----------------\n\n")
        # input()
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            output.write("Numar noduri maxime in memorie: " + str(nr_nod_max) + "\n")
            return 0, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
    nr_nod_total += len(lSuccesori)
    nr_nod_temp += len(lSuccesori)
    minim = float('inf')
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate, tip_euristica, nr_nod_total,
                                                  nr_nod_temp, nr_nod_max)
        if rez == "gata":
            return 0, "gata"
        # print("Compara ", rez, " cu ", minim)
        if rez < minim:
            minim = rez
            # print("Noul minim: ", minim)
    return nrSolutiiCautate, minim


# Argumente :
# 1 - Folder input
# 2 - Folder output
# 3 - NrSol
# 4 - Timeout (secunde)

director = sys.argv[1]
director_output = sys.argv[2]
count = 1
for fisier in os.listdir(director):
    if fisier[0] == '.':  # Daca nu dorim utilizarea unui input,
        continue  # ii punem un . in fata denumirii sale.
    locatie = os.path.join(director, fisier)
    locatie_output = os.path.join(director_output, "output" + str(count) + ".txt")
    count += 1
    if os.path.isfile(locatie):
        output = open(locatie_output, "w")
    else:
        output = open(locatie_output, "x")
        output = open(locatie_output, "w")

    output.write("Urmatoarele sunt solutiile pentru fisierul de input: " + locatie + "\n\n\n")

    gr = Graph(locatie)
    gr.nuAreSolutii(gr.start)
    nr_sol = int(sys.argv[3])
    timeout = float(sys.argv[4])

    # Rezolvat cu breadth first
    output.write("Solutii obtinute cu breadth first:\n")
    t1 = time.time()
    breadth_first(gr, nrSolutiiCautate=nr_sol)
    #
    output.write("\n\n##################\n\nSolutii obtinute cu Depth First:\n")
    t1 = time.time()
    depth_first(gr, nrSolutiiCautate=nr_sol)
    #
    output.write("\n\n##################\n\nSolutii obtinute cu Depth First Iterativ:\n")
    t1 = time.time()
    depth_first_iterativ(gr, nrSolutiiCautate=nr_sol)
    #
    output.write("\n\n##################\n\nSolutii obtinute cu A* - Banal:\n")
    t1 = time.time()
    a_star(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica banala")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu A* - Admisibil 1:\n")
    t1 = time.time()
    a_star(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica admisibila 1")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu A* - Neadmisibil:\n")
    t1 = time.time()
    a_star(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica neadmisibila")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu A* optimizat - Banal:\n")
    t1 = time.time()
    a_star_optimizat(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica banala")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu A* optimizat - Admisibil 1:\n")
    t1 = time.time()
    a_star_optimizat(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica admisibila 1")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu A* optimizat - Neadmisibil:\n")
    t1 = time.time()
    a_star_optimizat(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica neadmisibila")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu IDA* - Banal:\n")
    t1 = time.time()
    ida_star(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica banala")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu IDA* - Admisibila 1:\n")
    t1 = time.time()
    ida_star(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica admisibila 1")
    #
    output.write("\n\n##################\n\nSolutii obtinute cu IDA* - Neadmisibila:\n")
    t1 = time.time()
    ida_star(gr, nrSolutiiCautate=nr_sol, tip_euristica="euristica neadmisibila")

# To Do:
# Admisibila 2
# Documentatie pe baza rezultatelor
