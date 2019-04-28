#!venv/bin/python
import itertools
import pycosat as sat

import lib.file_io as fio


def sat_3sat(cnf, height, width):
    """
    Convertit une liste de clauses quelconques en des clauses 3-SAT.
    Format utilisé: liste dimacs compatible pycosat.
    """
    cnf_3sat = []  # nouvelle liste de clauses

    # calculer le 1e indice de variable qui est libre.
    i = 1 + 3 * (height + 2) * width

    for clause in cnf:
        if len(clause) == 1:
            # rajouter deux variables pour remplir
            # ex: (a) = (a+u+v)(a+u+-v)(a+-u+v)(a+-u+-v)
            cnf_3sat.append([clause[0], i, i + 1])
            cnf_3sat.append([clause[0], i, -(i + 1)])
            cnf_3sat.append([clause[0], -i, i + 1])
            cnf_3sat.append([clause[0], -i, -(i + 1)])
            i += 2
        elif len(clause) == 2:
            # rajouter une variable pour remplir
            # ex: (a+b) = (a+b+u)(a+b+-u)
            cnf_3sat.append([clause[0], clause[1], i])
            cnf_3sat.append([clause[0], clause[1], -i])
            i += 1
        elif len(clause) == 3:
            # ne rien rajouter, utiliser telle quelle la clause
            cnf_3sat.append(clause)
        else:
            # découper la clause
            # ex: (a+b+c+d+e) = (a+b+u)(-u+c+v)(-v+d+e)
            cnf_3sat.append([clause[0], clause[1], i])
            for k in range(1, len(clause) - 3):
                cnf_3sat.append([-i, clause[k + 1], i + 1])
                i += 1
            cnf_3sat.append([-i, clause[len(clause) - 2], clause[len(clause) - 1]])
    return cnf_3sat


def make_each_positive_once(zone, gridWidth, mode):
    """
    Pour chaque zone, on considère dans la première clause que chaques cases peuvent être un ballon (respectivement une pierre).
    Dans les clauses suivantes, on prend la négation du ième élément (compris entre le premier et l'avant-dernier), et on le distribue
    à chaque élément compris entre le ième+1 élément et le dernier en les mettant en négation et à chaque fois dans une nouvelle clause.
    
    Exemple :
    Zone = {(2,0), (2,1), (2,2)}}
    Clauses : 
    [B(2,0) + B(2,1) + B(2,2)] • 
    [-B(2,0) + -B(2,1)] • [-B(2,0) + -B(2,2)] •    <= le premier élément de la clause du dessus est B(2,0).
                                                      On prend donc sa négation puis la distribue sur chaque élément suivant
						      en les mettant dans une nouvelle clause.
    [-B(2,1) + -B(2,2)] •                          <= le second élément (et avant dernier) est B(2,1).
                                                      On prend sa négation puis la distribue sur la négation de l'élément suivant
						      qui est dans ce cas le dernier.
    
    [P(2,0) + P(2,1) + P(2,2)] •                   <= même principe mais pour les pierres.
    [-P(2,0) + -P(2,1)] • [-P(2,0) + -P(2,2)] • 
    [-P(2,1) + -P(2,2)] •
    
    Ce procédé est le même pour n'importe quelle taille de la première clause.
    """
    clause = []
    # chaque case pourrait être le ballon
    for i in range(len(zone)):
        j = 3 * gridWidth * (1 + zone[i][1]) + 1 + 3 * zone[i][0] + mode
        clause.append(j)
    yield clause

    # si la case de l est le ballon, alors les cases dea k ne peuvent pas
    # l'être, et ce pour tout k > l
    for i in range(len(zone) - 1):
        # l est positif
        l = 3 * gridWidth * (1 + zone[i][1]) + 1 + 3 * zone[i][0] + mode
        # chaque k est négatif
        for k in range(i + 1, len(zone)):
            clause = []
            j = 3 * gridWidth * (1 + zone[k][1]) + 1 + 3 * zone[k][0] + mode
            clause.append(-l)
            clause.append(-j)
            yield clause


def gen_cnf(width, height, zones, blacks):
    """
    Génère la forme normale conjonctive donnant la satisfaisabilité de la
    grille de Dosun-Fuwari donnée en argument.
    Format de sortie: liste d'entiers compatible avec pycosat.

    Arguments:
        - width: largeur de la grille
        - height: hauteur de la grille
        - zones: liste des zones de la grille
                 Format attendu: 
                 [
                    [[x1, y1], [x2,y2], ...],
                    [[x3, y3], [x4,y4], ...], 
                    ...
                 ]
        - blacks: liste des cases noires de la grille
                  Expected format:
                  [
                    [x1,y1],
                    [x2,y2],
                    ...
                  ]

    Règles logiques traduites:
        Chaque case de la grille a trois variables qui lui sont associées:
        isStone, isBalloon et isBlack. Pour une cellule donnée [x,y] de la
        grille appartenant à une zone donnée [[x,y], [xz1,yz1], [xz2,yz2]...],
        les règles déterminant sa légalité sont les suivantes:
          - Chaque pierre doit être placée sur une cellule noire ou sur une
            autre pierre:
                isStone(x,y) => isBlack(x, y+1) or isStone(x, y+1)
          - Chaque ballon doit être placée sous une cellule noire ou sous un
            autre ballon:
                isBalloon(x,y) => isBlack(x, y-1) or isBalloon(x, y-1)
          - Chaque zone doit contenir un unique ballon:
                isStone(x,y) and not isStone(xz1, yz1) and not
                isStone(xz2, yz2) and not isStone...
          - Chaque zone doit contenir une unique pierre:
                isBalloon(x,y) and not isBalloon(xz1, yz1) and not
                isBalloon(xz2, yz2) and not isBalloon...
    
    Convention de nommage des variables DIMACS:
        Les variables sont assignées par groupe de trois allant par rangée, du
        haut de la grille vers le bas, à partir de la rangée -1. Exemple:

	       (1,2,3)    (4,5,6)   (7,8,9) 
         ________________________________
        |          |          |          |       Ici, 45 : isBlack(3,4)
        | 10,11,12 | 13,14,15 | 16,17,18 |            10 : isBallon(0,0)
        |__________|__________|__________|            11 : isStone(0,0)
        |          |          |          |             1 : isBallon(0,-1)
        | 19,20,21 | 22,23,24 | 25,26,27 |            12 : isBlack(0,0)
        |__________|__________|__________| 
        |          |          |          | 
        | 28,29,30 | 31,32,33 | 34,35,36 | 
        |__________|__________|__________| 

	     (37,38,39) (40,41,42) (43,44,45)
    """
    cnf = []

    # Clauses pour les cases en dehors de la grille
    # Cases au dessus
    for i in range(1, 1 + 3 * width - 1, 3):
        cnf.append([-i])  # les cases au dessus ne peuvent contenir de ballon
        cnf.append([-(i + 1)])  # elles ne peuvent pas non plus contenir de pierre
        cnf.append([i + 2])  # Mais elles sont considérées noires
    # Cases en dessous: règles identiques que pour au dessus
    for i in range(
        3 * width * height + 3 * width + 1,                  # debut
        3 * width * height + 3 * width + 1 + 3 * width - 1,  # fin
        3,                                                   # pas
    ):
        cnf.append([-i])
        cnf.append([-(i + 1)])
        cnf.append([i + 2])

    # Clauses définissant les cases noires
    i = 1 + 3 * width
    for y in range(height):
        for x in range(width):
            if [x, y] in blacks:
                cnf.append([i + 2])     # (x,y) est noire
                cnf.append([-i])        # (x,y) ne peut pas contenir un ballon
                cnf.append([-(i + 1)])  # (x,y) ne peut pas contenir une pierre
            else:
                # (x,y) n'est pas noire: on ne sait donc pas si elle contient
                # un ballon ou une pierre
                cnf.append([-(i + 2)])
            i += 3

    # Une case ne peut pas contenir à la fois un ballon et une pierre
    for i in range(1 + 3 * width, 3 * width * height + 3 * width + 1, 3):
        cnf.append(
            [-i, -(i + 1)]
        )  # not(isBalloon and isStone) = not isBalloon or not isStone

    # Conditions de position des pierres
    # On s'arrête à la ligne height-1 vu que qu'une pierre dans la ligne du
    # bas repose forcément sur le bas de la grille: c'est donc forcément légal
    i = 1 + 3 * width
    for _ in range(0, height - 1):
        for _ in range(0, width):
            # not isStone(x,y) or isStone(x,y+1) or isBlack(x,y+1)
            cnf.append([-(i + 1), (i + 1) + 3 * width, (i + 1) + 3 * width + 1])
            i += 3
    # Conditions de position des ballons
    # On commence à la ligne 1 (2e ligne) vu que qu'un ballon dans la ligne du
    # haut repose forcément contre le haut de la grille: c'est donc forcément
    # légal
    i = 1 + 3 * width * 2
    for _ in range(0, height - 1):
        for _ in range(0, width):
            # not isBalloon(x,y) or isBalloon(x,y-1) or isBlack(x,y-1)
            cnf.append([-i, i - 3 * width, i - 3 * width + 2])
            i += 3
    # Conditions d'unicité des ballons et des pierres dans les zones
    for zone in zones:
        # Chaque case de la zone pourrait être un ballon
        for clause in make_each_positive_once(zone, width, 0): #0 = mode ballon
            cnf.append(list(clause))
        # Chaque case de la zone pourrait être une pierre
        for clause in make_each_positive_once(zone, width, 1): #1 = mode pierre
            cnf.append(list(clause))
    return cnf
