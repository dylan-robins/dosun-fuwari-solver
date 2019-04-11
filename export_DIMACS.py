def gen_dimacs(ncf):
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
    fichier = open("fichier_dimacs.cnf", "w")
    fichier.write("c Creation du fichier DIMACS avec les clauses \n")
    fichier.write("p cnf ")
    fichier.write(str(nb_variables))
    fichier.write(" ")
    fichier.write(str(nb_clauses))
    fichier.write("\n")
    for clause in ncf:
        for variable in clause:
            fichier.write(str(variable))
            fichier.write(" ")
        fichier.write("\n")
    fichier.close()