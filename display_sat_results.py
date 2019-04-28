#!venv/bin/python
from sys import argv, stdin, stderr
from lib.file_io import read_grid


def interpret_results(clause, gridWidth, gridHeight):
    """
    Affiche dans la ligne de commade une grille de Dosum Fuwari résolue sous
    forme textuelle à partir de la clause fournie par le satsolver.
    Arguments:
      - clause: variables rendues par le satsolver définissant les positions
                des cases noires, des ballons et des pierres.
                Format attendu: liste d'entiers. Ex: [-1, 2, -3,...]
    Symboles utilisés pour l'affichage:
      - 'B' = ballon
      - 'S' = pierre (stone)
      - 'N' = case noire
      - '-' = case vide
    """
    # Parcourir la clause en ignorant les variables en dehors de la grille
    # servant uniquement pour résoudre le problème
    x = 0  # colonne courante
    y = 0  # ligne courante
    # La première variable dans la grille (la case en haut à gauche) est
    # précédée par une ligne entière de variables
    i = gridWidth * 3

    # On ne sait pas combien de variables le satsolver a rajouté dans la
    # clause pour résoudre le problème, on doit donc compter les lignes pour
    # savoir où s'arrêter
    while y < gridHeight:
        if clause[i] > 0:
            # Afficher un ballon
            print("B", end=" ")
        elif clause[i + 1] > 0:
            # afficher une pierre
            print("S", end=" ")
        elif clause[i + 2] > 0:
            # afficher une case noire
            print("N", end=" ")
        else:
            # afficher une case vide
            print("-", end=" ")
        i += 3 # passer au groupe de variables suivante
        x += 1 # passer à la colonne suivante
        if x >= gridWidth:
            # si on est arrivé en bout de ligne, afficher un retour à ligne
            print("")
            # repasser à la premièrecolonne et passer à la ligne suivante
            x = 0
            y += 1
    # terminer l'affichage par une ligne pour bien marquer que c'est la fin de la grille
    print(
        "________________________________________________________________________________\n"
    )


if __name__ == "__main__":
    if len(argv) < 3:
        print("Error: incorrect number of arguments", file=stderr)
        print(
            "Usage: {} <name of satsolver> path/to/grid/file path/to/sat/output/file".format(
                argv[0]
            ),
            file=stderr,
        )
        print("Supported satsolvers: minisat, picosat", file=stderr)
        print("Sat output can be read from stdin", file=stderr)
        exit(1)

    # Lire la grille
    grid = read_grid(argv[2])

    # Ouvrir le fichier sat
    if len(argv) == 3:
        satfile = stdin
    else:
        satfile = open(argv[3], "r")

    content = satfile.read()  # Lire le contenu

    # Fermer le fichier
    if len(argv) > 2:
        satfile.close()

    # Parser le contenu
    if argv[1] == "minisat":
        # Minisat ne fournit qu'une solution à la fois, et le format de fichier est très simple:
        # La première ligne contient "SAT\n" si le problème est satisfaisable, et la 2e ligne
        # contient la solution
        satisfiability = content.split("\n", 1)[0]
        solutions = content.split("\n", 1)[1]

        if satisfiability == "SAT":
            solutions = solutions.split("\n")
            # se débarasser de potentielles listes vides causées par le split qui agit en fin de ligne
            solutions = [line for line in solutions if line != ""]
            # convertir la solution (chaine de caractères) en liste d'entiers
            solutions = [list(map(int, line.split(" "))) for line in solutions]
            print("S : stone\nB : balloon\nN : black cell\n- : empty cell\n")
            print("{} solutions found:".format(len(solutions)))
        else:
            print("No solutions found")
            exit(0)

    elif argv[1] == "picosat":
        # l'affichage de sortie de picosat est plus compliqué: si le problème est satisfaisable
        # la 1e ligne contiendra "s SATISFIABLE\n". Les lignes suivantes contiennent alors une
        # solution au problème, avec un renvoi à la ligne automatique à 79 caractères, avec chaque
        # ligne préfixée par "v ". De plus chaque solution trouvée est précédée par la même ligne
        # "s SATISFIABLE\n". Et en plus si plusieurs solutions ont été trouvées la dernière ligne
        # du fichier contiendra le nombre de solutions "s SOLUTIONS ..." avec ... le nombre de
        # solutions
        satisfiability = content.split("\n", 1)[0]  # récupérer la 1e ligne

        if satisfiability == "s SATISFIABLE":
            # supprimer les lignes qui séparent les solutions
            solutions = content.replace("s SATISFIABLE\n", "")
            solutions = solutions.split("s SOLUTIONS ", 1)[
                0
            ]  # se débarasser du nombre de solutions
            solutions = solutions.replace(
                "v ", ""
            )  # supprimer tous les "v " en début de ligne
            solutions = solutions.replace(
                "\n", " "
            )  # recoller toutes les lignes ensemble
            solutions = solutions.split(" 0 ")  # couper la liste à chaque 0
            # se débarasser de potentielles listes vides causées par le split qui agit en fin de ligne
            solutions = [line for line in solutions if line != ""]
            # convertir la solution (chaine de caractères) en liste d'entiers
            solutions = [list(map(int, line.split(" "))) for line in solutions]
            print("{} solutions found:".format(len(solutions)))
        else:
            print("No solutions found")
            exit(0)

    # Afficher les solutions
    for line in solutions:
        interpret_results(line, grid["width"], grid["height"])
