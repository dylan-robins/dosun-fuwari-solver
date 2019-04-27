import json

def save_grid(grid, path):
    """
    Enregistre la grille fournie en 1e argument dans le fichier fourni en
    2e argument au format JSON.
    Format de grille attendu:
    {
        "width": largeur de la grille (entier),
        "height": hauteur de la grille (entier),
        "blacks": [[x1, y1], [x2, y2], ...] les coordonnées des cellules noires
        "zones" : [
            [[x1, y1], [x2, y2], ...], les coordonnées des cellules de la zone 1
            [[x3, y3], [x4, y4], ...], les coordonnées des cellules de la zone 2
            ...
        ]
    }
    """
    with open(path, "w") as in_file:
        in_file.write(json.dumps(grid))

def read_grid(path):
    """
    Charge depuis le fichier JSON fourni en argument une grille, renvoyée
    comme un dictionnaire python.
    Format de grille attendu:
    {
        "width": largeur de la grille (entier),
        "height": hauteur de la grille (entier),
        "blacks": [[x1, y1], [x2, y2], ...] les coordonnées des cellules noires
        "zones" : [
            [[x1, y1], [x2, y2], ...], les coordonnées des cellules de la zone 1
            [[x3, y3], [x4, y4], ...], les coordonnées des cellules de la zone 2
            ...
        ]
    }
    """
    with open(path, "r") as in_file:
        grid = json.loads(in_file.read())
    return grid

def save_dimacs(cnf, filename):
    """
    Enregistre les clauses fournies en 1e argument dans le fichier fourni en
    2e argument au format DIMACS.
    Format de clauses attendu: liste d'entiers (format dimacs compatible avec
    pycosat)
    """
    #Initialisation du nombre de clause
    nb_clauses = 0
    #Initialisation d'une liste pour chercher le nombre de variables de la formule
    unique_variables=[]

    for clause in cnf:
        # incrémenter le nombre de clauses
        nb_clauses+=1
        # Pour chaque variable, si elle n'est pas dans unique_variables, incrementer
        # le compteur du nombre de variable et l'ajouter dans unique_variables
        for variable in clause:
            if not(variable in unique_variables) and not(-variable in unique_variables):
                unique_variables.append(variable)
    
    #Ecriture du le fichier au format DIMACS
    with open(filename, "w") as fichier:
        # En-tête
        fichier.write("c Creation du fichier DIMACS avec les clauses\n")
        fichier.write("p cnf ")
        fichier.write(str(len(unique_variables)))
        fichier.write(" ")
        fichier.write(str(nb_clauses))
        fichier.write("\n")
        # Clauses
        for clause in cnf:
            i = 1
            for variable in clause:
                fichier.write(str(variable))
                fichier.write(" ")
                if i == len(clause):
                    fichier.write("0") # une clause dimacs est terminée par un 0
                i += 1
            fichier.write("\n")
