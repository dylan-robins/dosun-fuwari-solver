#!venv/bin/python
from sys import argv, stderr
from lib.file_io import read_grid, save_dimacs
from lib.gen_formule import gen_cnf

if __name__ == "__main__":
    # vérification du nombre d'arguments
    if len(argv) < 2:
        print("Erreur: veuillez fournir au moins une grille en argument", file=stderr)
        print("Usage: {} path/to/grid.json path/to/another/grid.json ....".format(argv[0]), file=stderr)
        exit(1)
        
    # convertir chaque grille fournie en argument et les exporter au format DIMACS
    for i in range(1, len(argv)):
        # lire la grille
        grid = read_grid(argv[i])
        # générer les clauses
        cnf = gen_cnf(grid["width"], grid["height"], grid["zones"], grid["blacks"])
        # générer le nom du fichier de sortie
        output_filename = argv[i].split(".json")[0] + ".cnf"
        # exporter au format DIMACS
        save_dimacs(cnf, output_filename)

    