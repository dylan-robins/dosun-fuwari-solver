#!venv/bin/python
from sys import argv, stdin, stderr
from lib.file_io import read_grid

def interpret_results(clause, gridWidth, gridHeight):
    """
    Print to the terminal the grid described by the clause given as argument.
    Symbols used: B = balloon, S = stone, N = black cell (Noir), - = free cell
    """
    x = 0
    y = 0
    i = gridWidth*3
    while i < len(clause)-gridWidth*3:
        if x >= gridWidth:
            # print a newline and check if we've reached the end
            print("") # newline
            x = 0
            y += 1
            if y > gridHeight-1:
                break
        if clause[i] > 0:
            # print a balloon
            print("B", end=" ")
        elif clause[i+1] > 0:
            # print a stone
            print("S", end=" ")
        elif clause[i+2] > 0:
            # print a black (Noir) cell
            print("N", end=" ")
        else:
            # print a free cell
            print("-", end=" ")
        i += 3
        x += 1
    print("\n________________________________________________________________________________\n")


if __name__ == "__main__":
    if len(argv) < 3:
        print("Error: incorrect number of arguments", file=stderr)
        print("Usage: {} <name of satsolver> path/to/grid/file path/to/sat/output/file".format(argv[0]), file=stderr)
        print("Supported satsolvers: minisat, picosat", file=stderr)
        print("Satsolver output can be read from stdin", file=stderr)
        exit(1)

    # Lire la grille
    grid = read_grid(argv[2])

    # Ouvrir le fichier sat
    if len(argv) == 3:
        satfile = stdin
    else:
        satfile = open(argv[3], "r")
    
    content = satfile.read() # Lire le contenu
    
    # Fermer le fichier
    if len(argv) > 2:
        satfile.close()
    
    # Parser le contenu
    if argv[1] == "minisat":
        # Minisat ne fournit qu'une solution à la fois, et le format de fichier est très simple:
        # La première ligne contient "SAT\n" si le problème est satisfaisable, et la 2e ligne
        # contient la solution
        satisfiability = content.split('\n', 1)[0]
        solutions = content.split('\n', 1)[1]
        
        if satisfiability == "SAT\n":
            solutions = solutions.split("\n")
            # se débarasser de potentielles listes vides causées par le split qui agit en fin de ligne
            solutions = [line for line in solutions if line != '']
            # convertir la solution (chaine de caractères) en liste d'entiers
            solutions = [list(map(int, line.split(" "))) for line in solutions]
            
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
        satisfiability = content.split('\n', 1)[0] # récupérer la 1e ligne
        
        if satisfiability == "s SATISFIABLE":
            # supprimer les lignes qui séparent les solutions
            solutions = content.replace('s SATISFIABLE\n', '')
            solutions = solutions.split("s SOLUTIONS 3", 1)[0] # se débarasser du nombre de solutions
            solutions = solutions.replace("v ", "") # supprimer tous les "v " en début de ligne
            solutions = solutions.replace("\n", " ") # recoller toutes les lignes ensemble
            solutions = solutions.split(" 0 ") # couper la liste à chaque 0
            # se débarasser de potentielles listes vides causées par le split qui agit en fin de ligne
            solutions = [line for line in solutions if line != '']
            # convertir la solution (chaine de caractères) en liste d'entiers
            solutions = [list(map(int, line.split(" "))) for line in solutions]
            print("{} solutions found:".format(len(solutions)))
        else:
            print("No solutions found")
            exit(0)
        
    # Afficher les solutions
    for line in solutions:
        interpret_results(line, grid["width"], grid["height"])