import json

def save_grid(grid, path):
    """
    Saves a grid to a file, 
    """
    with open(path, "w") as in_file:
        in_file.write(json.dumps(grid))

def read_grid(path):
    with open(path, "r") as in_file:
        grid = json.loads(in_file.read())
    return grid

def save_dimacs(ncf, filename):
    #Initialisation des compteurs du nombre de clause et du nombre de variables de la formule
    nb_clauses = 0
    nb_variables = 0
    #Initialisation d'une liste pour chercher le nombre de variables de la formule
    tab=[]
    #Pour chaques clauses incrementer le compteur du nombre de clauses
    for clause in ncf:
        nb_clauses+=1
        #Pour chaque variable, si elle n'est pas dans tab, incrementer le compteur du nombre de variable et l'ajouter dans tab
        for variable in clause:
            if not(variable in tab) and not(-variable in tab):
                nb_variables+=1
                tab.append(variable)
    #Ecriture dans le fichier au format DIMACS
    fichier = open(filename, "w")
    fichier.write("c Creation du fichier DIMACS avec les clauses\n")
    fichier.write("p cnf ")
    fichier.write(str(nb_variables))
    fichier.write(" ")
    fichier.write(str(nb_clauses))
    fichier.write("\n")
    for clause in ncf:
        i = 1
        for variable in clause:
            fichier.write(str(variable))
            fichier.write(" ")
            if i == len(clause):
                fichier.write("0")
            i += 1
        fichier.write("\n")
    fichier.close()

if __name__ == "__main__":
    grid = {
        'width': 3,
        'height': 3,
        'zones': [
            [(0,0),(1,0)],
            [(1,1),(0,1),(1,2)],
            [(2,0),(2,1),(2,2)]
        ],
        'blacks': [
            (0,1)
        ]
    }
    save_grid(grid, "grid_3x3.json")
    contents = read_grid("grid_3x3.json")
    
    print("input:", grid)
    print("output:", contents)
