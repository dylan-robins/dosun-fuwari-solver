from tkinter import *
from tkinter.ttk import *
import pycosat as sat

from lib.gen_formule import gen_cnf, sat_3sat


class Grid(Canvas):
    """
    Classe définissant une grille de Dosun Fuwari intéractive.
    """

    cell_width = 50
    border_width = 4

    def __init__(self, x, y, solvable_textvar, blacks=[], zones=[], master=None):
        """
        Initialisation automatique à la création d'une grille
        Arguments:
          - x : largeur de la grille
          - y : hauteur de la grille
          - solvable_textvar: TextVar contenant le message de satisfaisabilité
                              de la grille (à mettre à jour après résolution
                              de la grille)
          - blacks (optionnel): Liste des cases noires de la grille
                                préexistante à afficher
          - zones (optionnel): Liste des zones de la grille préexistante à
                               afficher
          - master (optionnel): Element Tk dans lequel dessiner la grille
        """
        # Initialiser les variables d'instance
        self.master = master
        self.dimensions = (x, y)
        self.black_cells = blacks
        self.zones = zones
        self.solvable_textvar = solvable_textvar
        # Initialiser le canvas
        super().__init__(
            master,
            width=x * self.cell_width + self.border_width,
            height=y * self.cell_width + self.border_width,
        )
        # Dessiner la grille vide
        self.draw()

        # Dessiner la grille fournie (si fournie)
        if zones != [] or blacks != []:
            self.load_grid(zones, blacks)

    def draw(self):
        """
        Dessiner une grille vide
        """
        # Dessiner les cases
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                self.create_rectangle(
                    x * self.cell_width + self.border_width,
                    y * self.cell_width + self.border_width,
                    (x + 1) * self.cell_width,
                    (y + 1) * self.cell_width,
                    fill="white",
                    width=0.0,
                    tags="cell x" + str(x) + " y" + str(y),
                )
        # Assigner à chaque case l'action toggle_selected_tag
        self.tag_bind("cell", "<ButtonPress-1>", self.toggle_selected_tag)

        # Dessiner les bordures horizontales
        for y in range(self.dimensions[1] + 1):
            for x in range(self.dimensions[0] + 1):
                self.create_rectangle(
                    x * self.cell_width,
                    y * self.cell_width,
                    (x + 1) * self.cell_width + 2 * self.border_width,
                    y * self.cell_width + self.border_width,
                    fill="#aaaaaa",
                    width=0.0,
                    tags="border horizontal x" + str(x) + " y" + str(y),
                )
        # Dessiner les bordures verticales
        for y in range(self.dimensions[1] + 1):
            for x in range(self.dimensions[0] + 1):
                self.create_rectangle(
                    x * self.cell_width,
                    y * self.cell_width,
                    x * self.cell_width + self.border_width,
                    (y + 1) * self.cell_width + self.border_width,
                    fill="#aaaaaa",
                    width=0.0,
                    tags="border vertical x" + str(x) + " y" + str(y),
                )

    def find_selected_neighbours(self, cell, found=set()):
        """
        Trouver les voisins sélectionnés de la case donnée en argument,
        ainsi que les voisins sélectionnés de chacun d'entre eux etc
        récursivement.
        Arguments:
          - cell: case à partir de laquelle on cherche les voisins
          - found (optionnel): ensemble des voisins connus. Nécessaire pour ne
                               pas revenir en arrière lors de la récursion.
                               Initialement devrait être vide.
        """
        # vérifier que cell est bien sélectionnée
        tags = self.gettags(cell)
        if "selected" in tags:
            # l'ajouter à l'ensemble
            found.add(cell)
            # trouver ses coordonnées pour trouver tous ses voisins
            x = int(tags[1][1:])
            y = int(tags[2][1:])
            neighbours = self.find_neighbours(x, y)
            # ne garder que les voisins sélectionnés et tous leurs voisins
            # sélectionnés
            for ncell in neighbours:
                if neighbours[ncell] not in found:
                    for u in self.find_selected_neighbours(neighbours[ncell], found):
                        found.add(u)
        return found

    def toggle_selected_tag(self, event):
        """
        Ajoute la case sur laquelle l'utilisateur a cliqué à la sélection. Si
        la case était déjà sélectionnée, on la déselectionne à la place. Si
        la déselectionner couperait la sélection en deux zones séparées, on
        désélectionne tout (par sécurité).
        Les cases sélectionnées sont colorées en bleu clair (#b3e5fc).
        """
        # Trouver les coordonnées de la case cliquée
        tags = self.gettags("current")
        x = int(tags[1][1:])
        y = int(tags[2][1:])

        # Si elle était déja sélectionnée, la déselectionner
        if "selected" in tags:
            self.dtag("current", "selected")
            # la recolorer de la bonne facon
            if "solid" in tags:
                self.itemconfig("current", fill="#000000")
            else:
                self.itemconfig("current", fill="#ffffff")

            # Vérifier si la sélection a été coupée en deux zones distinctes
            
            # On compare la sélection entière avec l'ensemble des cases
            # sélectionnées qui sont en contact avec la case de
            # la sélection. Si les deux ensembles ne sont pas égaux, alors
            # la sélection a été coupée
            # sélection entière

            # Si la sélection est vide ca sert à rien
            selection = self.find_withtag("selected")
            if len(selection) > 0:
                # partie de la sélection en contact avec le 1e élement de la
                # liste précédente
                selection_contiguous = self.find_selected_neighbours(selection[0])
                # si les deux ensembles sont différents, tout désélectionner
                if set(selection) != selection_contiguous:
                    self.itemconfig("selected", fill="#ffffff")
                    self.itemconfig("solid", fill="#000000")
                    self.dtag("selected", "selected")

        # Sinon ajouter la case cliquée à la sélection (si c'est autorisé)
        else:
            # vérifier si elle partage une bordure avec la sélection existante
            # trouver ses voisins, vérifier si l'un d'entre eux est sélectionné
            neighbours = self.find_neighbours(x, y)
            has_selected_neighbour = False
            for cell in neighbours:
                if "selected" in self.gettags(neighbours[cell]):
                    has_selected_neighbour = True
                    break

            # Si non, tout déselectionner et garder que la nouvelle case
            if not has_selected_neighbour:
                self.itemconfig("selected", fill="#ffffff")
                self.itemconfig("solid", fill="#000000")
                self.dtag("selected", "selected")

            # Sélectionner la case et la colorer en bleu
            self.addtag_withtag("selected", "current")
            self.itemconfig("selected", fill="#b3e5fc")

    def find_neighbours(self, x, y):
        """
        Trouve les cases voisines de la case (x,y)
        Renvoie un dictionaire des éléments Tk des voisins
        Format:
        {
            "up": id de l'élément du canvas (entier),
            "down": id de l'élément du canvas (entier),
            "left": id de l'élément du canvas (entier),
            "right": id de l'élément du canvas (entier)
        }
        """
        # Trouver toutes les cases
        cells = self.find_withtag("cell")
        neighbours = {}
        # Pour chaque case de la grille, si la case a les bonnes coordonnées,
        # l'ajouter au dict
        for cell in cells:
            cell_tags = self.gettags(cell)
            # Voisin gauche
            if "x" + str(x - 1) in cell_tags and "y" + str(y) in cell_tags:
                neighbours["left"] = cell
            # Voisin supérieur
            if "x" + str(x) in cell_tags and "y" + str(y - 1) in cell_tags:
                neighbours["up"] = cell
            # Voisin droit
            if "x" + str(x + 1) in cell_tags and "y" + str(y) in cell_tags:
                neighbours["right"] = cell
            # Voisin inférieur
            if "x" + str(x) in cell_tags and "y" + str(y + 1) in cell_tags:
                neighbours["down"] = cell
        return neighbours

    def make_zone_from_selection(self):
        """
        Créé une zone à partir de la sélection courante.
        """
        # Trouver les cases sélectionnées
        selection = self.find_withtag("selected")
        borders = self.find_withtag("border")
        # Ajouter une zone dans la liste
        self.zones.append([])
        for item in selection:
            # Trouver les coordonnées de la case courante
            tags = self.gettags(item)
            x = int(tags[1][1:])
            y = int(tags[2][1:])
            if "solid" in tags:
                self.dtag(item, "solid")
                self.black_cells.remove([x, y])
            # Trouver ses voisins
            neighbours = self.find_neighbours(x, y)
            # Ne garder que ceux qui sont sélectionnés
            for cell in list(neighbours):
                tags = self.gettags(neighbours[cell])
                if "selected" not in tags:
                    del neighbours[cell]
            # Colorier ses bordures
            for border in borders:
                border_tags = self.gettags(border)
                # bordure gauche
                if (
                    "x" + str(x) in border_tags
                    and "y" + str(y) in border_tags
                    and "vertical" in border_tags
                ):
                    if "left" not in neighbours.keys():
                        self.itemconfig(border, fill="#000000")
                    else:
                        self.itemconfig(border, fill="#aaaaaa")
                # bordure supérieure
                elif (
                    "x" + str(x) in border_tags
                    and "y" + str(y) in border_tags
                    and "horizontal" in border_tags
                ):
                    if "up" not in neighbours.keys():
                        self.itemconfig(border, fill="#000000")
                    else:
                        self.itemconfig(border, fill="#aaaaaa")
                # bordure droite
                elif (
                    "x" + str(x + 1) in border_tags
                    and "y" + str(y) in border_tags
                    and "vertical" in border_tags
                ):
                    if "right" not in neighbours.keys():
                        self.itemconfig(border, fill="#000000")
                    else:
                        self.itemconfig(border, fill="#aaaaaa")
                # bordure inférieure
                elif (
                    "x" + str(x) in border_tags
                    and "y" + str(y + 1) in border_tags
                    and "horizontal" in border_tags
                ):
                    if "down" not in neighbours.keys():
                        self.itemconfig(border, fill="#000000")
                    else:
                        self.itemconfig(border, fill="#aaaaaa")

            # Retirer l'item de toute autre zone
            for zone in self.zones:
                if [x, y] in zone:
                    zone.remove([x, y])
            # L'ajouter à la nouvelle zone
            self.zones[-1].append([x, y])
            # Retirer les zones vides
            for zone in self.zones:
                if zone == []:
                    self.zones.remove(zone)
        # désélectionner les cases
        self.itemconfig("selected", fill="#ffffff")
        self.itemconfig("solid", fill="#000000")
        self.dtag("selected", "selected")

    def toggle_selection_solid(self):
        """
        Rend solide toutes les cases sélectionnées
        """
        # trouver toutes les cases sélectionnées
        selection = self.find_withtag("selected")
        for cell in selection:
            # vérifier si la case est déjà solide
            tags = self.gettags(cell)
            if "solid" in tags:
                # Si oui, la remettre vide
                self.black_cells.remove([int(tags[1][1:]), int(tags[2][1:])])
                self.dtag(cell, "solid")
                self.itemconfig(cell, fill="#ffffff")
            else:
                # Sinon la rendre solide
                self.black_cells.append([int(tags[1][1:]), int(tags[2][1:])])
                self.addtag_withtag("solid", cell)
                self.itemconfig(cell, fill="#000000")
        # Tout déselectionner
        self.dtag("selected", "selected")

    def solve(self):
        """
        Résoudre la grille, dessiner la solution et afficher le résultat dans
        le champs de texte prévu pour.
        """
        # Rendre la grille non modifiable une fois qu'elle a été résolue
        self.tag_unbind("cell", "<ButtonPress-1>")
        # Afficher un message des fois que la recherche d'une solution mette
        # un peu de temps
        self.solvable_textvar.set("Looking for solution...")
        # Générer les clauses
        cnf = gen_cnf(
            self.dimensions[0], self.dimensions[1], self.zones, self.black_cells
        )
        # Convertir les clauses en 3-sat
        cnf = sat_3sat(cnf, self.dimensions[1], self.dimensions[0])
        # Trouver une solution
        solution = sat.solve(cnf)
        # Si une solution a été trouvée, l'afficher et mettre à jour le texte
        if not (solution == "UNSAT" or solution == "UNKNOWN"):
            self.draw_solution(solution)
            self.solvable_textvar.set("Solution found!")
        # Sinon, juste mettre a jour le texte
        else:
            self.solvable_textvar.set("No solution found!")

    def get_grid(self):
        """
        Renvoyer le dictionnaire définissant les propriétés de la grille.
        Format du dictionnaire renvoyé:
        {
            "width": largeur de la grille (entier),
            "height": hauteur de la grille (entier),
            "zones" : [
                [[x1, y1], [x2, y2], ...], les coordonnées des cellules de la zone 1
                [[x3, y3], [x4, y4], ...], les coordonnées des cellules de la zone 2
                ...
            ],
            "blacks": [[x1, y1], [x2, y2], ...] les coordonnées des cellules noires
        }
        """
        grid = {
            "width": self.dimensions[0],
            "height": self.dimensions[1],
            "zones": self.zones,
            "blacks": self.black_cells,
        }
        return grid

    def draw_solution(self, solution):
        """
        Dessiner la solution de la grille: les pierres sont symbolisées par
        des cercles noirs, les ballons par des cercles blancs.
        Format attendu de la solution: liste d'entiers telle que renvoyée par
        pycosat.
        """
        # Parcourir la clause en ignorant les variables en dehors de la grille
        # servant uniquement pour résoudre le problème
        x = 0  # colonne courante
        y = 0  # ligne courante
        # La première variable dans la grille (la case en haut à gauche) est
        # précédée par une ligne entière de variables
        i = self.dimensions[0] * 3
        # On ne sait pas combien de variables le satsolver a rajouté dans la
        # clause pour résoudre le problème, on doit donc compter les lignes pour
        # savoir où s'arrêter
        while y < self.dimensions[1]:
            if solution[i] > 0:
                # Dessiner un ballon
                self.create_oval(
                    self.cell_width * x + 5,
                    self.cell_width * y + 5,
                    self.cell_width * (x + 1) - 5,
                    self.cell_width * (y + 1) - 5,
                    fill="white",
                    width=2.0,
                )
            elif solution[i + 1] > 0:
                # Dessiner une pierre
                self.create_oval(
                    self.cell_width * x + 5,
                    self.cell_width * y + 5,
                    self.cell_width * (x + 1) - 5,
                    self.cell_width * (y + 1) - 5,
                    fill="black",
                    width=2.0,
                )

            i += 3 # passer au groupe de variables suivante
            x += 1 # passer à la colonne suivante

            if x >= self.dimensions[0]:
                # si on est arrivé en bout de ligne, repasser à la première
                # colonne et passer à la ligne suivante
                x = 0
                y += 1

    def load_grid(self, zones, blacks):
        """
        Charger les zones et les cases noires fournies en argument
        """
        # récupérer la liste des cases de la grille
        cells = self.find_withtag("cell")

        # dessiner les cases noires: les sélectionner toutes, les rendre noires
        # et les désélectionner
        for cell in blacks:
            for id in cells:
                tags = self.gettags(id)
                if ("x{}".format(cell[0]) in tags) and ("y{}".format(cell[1]) in tags):
                    self.addtag_withtag("selected", id)
        self.toggle_selection_solid()
        self.dtag("selected", "selected")

        # dessiner les zones: sélectionner chaque zone puis appeller la
        # fonction make_zone_from_selection()
        for zone in list(zones):
            # list() est nécessaire parce que la zones se fait modifier en
            # cours de route: en appelant list() dessus on force une copie de
            # la liste qui ne se fait donc pas modifier
            for cell in zone:
                for id in cells:
                    tags = self.gettags(id)
                    if ("x{}".format(cell[0]) in tags) and (
                        "y{}".format(cell[1]) in tags
                    ):
                        self.addtag_withtag("selected", id)
            self.make_zone_from_selection()
            # la fonction désélectionne toute seule la zone à la fin: pas
            # besoin de le faire ici
