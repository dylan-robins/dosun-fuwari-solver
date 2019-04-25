from tkinter import *
from tkinter.ttk import *
import pycosat as sat
from gen_formule import gen_ncf


class Grid(Canvas):
    cell_width = 50
    border_width = 4

    def __init__(self, x, y, solvable_textvar, blacks=[], zones=[], master=None):
        """ Initialisation automatique à la création d'une grille
            Prend en argument les dimensions x, y voulues de la grille """
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
        # Initialiser la grille
        self.draw()

        # Dessiner la grille fournie (si fournie)
        if zones != [] or blacks != []:
            self.load_grid(zones, blacks)

    def draw(self):
        """ Dessiner la grille """
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
        # Assigner à chaque cellule l'action toggle_selected_tag
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

    def find_selected_neighbours(self, cell, found):
        """
        Find selected neighbours and each of their selected neighbours etc...
        """
        tags = self.gettags(cell)
        if "selected" in tags:
            found.add(cell)
            x = int(tags[1][1:])
            y = int(tags[2][1:])
            neighbours = self.find_neighbours(x,y)
            for ncell in neighbours:
                if neighbours[ncell] not in found:
                    for u in self.find_selected_neighbours(neighbours[ncell], found):
                        found.add(u)
        return found

    def toggle_selected_tag(self, event):
        """
        Adds the cell the user clicked on to the selection. If clicked cell
        was already selected, deselects it. If deseletion splits the selected
        area into multiple parts, then deselects everything. Selected cells
        have the "selected" tag and are colored #b3e5fc (light blue). 
        """
        tags = self.gettags("current")
        # Find clicked cell's coordinates
        x = int(tags[1][1:])
        y = int(tags[2][1:])

        # If current cell was already selected, deselect it
        if "selected" in tags:
            self.dtag("current", "selected")
            if ("solid" in tags):
                self.itemconfig("current", fill="#000000")
            else:
                self.itemconfig("current", fill="#ffffff")

            # If selection has been split, then deselect everything.
            selection = self.find_withtag("selected")
            # If selection isn't empty, find all selected cells that share a
            # border with the 1st selected cell. If the two sets are different,
            # then the selection has been split
            if len(selection) > 0:
                selection_contiguous = self.find_selected_neighbours(selection[0], set())
                if set(selection) != selection_contiguous:
                    self.itemconfig("selected", fill="#ffffff")
                    self.itemconfig("solid", fill="#000000")
                    self.dtag("selected", "selected")

        # Add current cell to selection
        else:
            # check if neighbouring cells are in the current selection
            neighbours = self.find_neighbours(x, y)
            has_selected_neighbour = False
            for cell in neighbours:
                if "selected" in self.gettags(neighbours[cell]):
                    has_selected_neighbour = True
                    break
            
            # If not, deselect everything
            if not has_selected_neighbour:
                self.itemconfig("selected", fill="#ffffff")
                self.itemconfig("solid", fill="#000000")
                self.dtag("selected", "selected")
            
            # Add current cell to selection
            self.addtag_withtag("selected", "current")
            self.itemconfig("selected", fill="#b3e5fc")

    def find_neighbours(self, x, y):
        """ Trouve les cellules voisines de la cellule (x,y)
            Renvoie un dictionaire des éléments Tk des voisins """
        # Trouver toutes les cellules
        cells = self.find_withtag("cell")
        neighbours = {}
        # Pour chaque cellule de la grille, si la cellule a les bonnes
        # coordonnées, l'ajouter au dict
        for cell in cells:
            cell_tags = self.gettags(cell)
            # Si voisin gauche
            if "x" + str(x - 1) in cell_tags and "y" + str(y) in cell_tags:
                neighbours["left"] = cell
            # Si voisin supérieur
            if "x" + str(x) in cell_tags and "y" + str(y - 1) in cell_tags:
                neighbours["up"] = cell
            # Si voisin droit
            if "x" + str(x + 1) in cell_tags and "y" + str(y) in cell_tags:
                neighbours["right"] = cell
            # Si voisin inférieur
            if "x" + str(x) in cell_tags and "y" + str(y + 1) in cell_tags:
                neighbours["down"] = cell
        return neighbours

    def make_zone_from_selection(self):
        """ Créé une zone à partir de la sélection courante """
        # Trouver les items sélectionnés
        selection = self.find_withtag("selected")
        borders = self.find_withtag("border")
        # Ajouter une zone dans la liste
        self.zones.append([])
        for item in selection:
            # Trouver les coordonnées de l'item
            tags = self.gettags(item)
            x = int(tags[1][1:])
            y = int(tags[2][1:])
            if ("solid" in tags):
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
        """ Rend solide toutes les cellules sélectionnées """
        selection = self.find_withtag("selected")
        for cell in selection:
            tags = self.gettags(cell)
            if "solid" in tags:
                self.black_cells.remove([int(tags[1][1:]), int(tags[2][1:])])
                self.dtag(cell, "solid")
                self.itemconfig(cell, fill="#ffffff")
            else:
                self.black_cells.append([int(tags[1][1:]), int(tags[2][1:])])
                self.addtag_withtag("solid", cell)
                self.itemconfig(cell, fill="#000000")
        self.dtag("selected", "selected")

    def solve(self):
        self.tag_unbind("cell", "<ButtonPress-1>")
        self.solvable_textvar.set("Looking for solution...")
        ncf = gen_ncf(
            self.dimensions[0], self.dimensions[1], self.zones, self.black_cells)
        solution = sat.solve(ncf)
        if not (solution == "UNSAT" or solution == "UNKNOWN"):
            self.draw_solution(solution)
            self.solvable_textvar.set("Solution found!")
        else:
            self.solvable_textvar.set("No solution found!")

    def get_grid(self):
        grid = {
            'width': self.dimensions[0],
            'height': self.dimensions[1],
            'zones': self.zones,
            'blacks': self.black_cells
        }
        return grid

    def draw_solution(self, solution):
        x = 0
        y = 0
        i = self.dimensions[0]*3
        while i < len(solution)-self.dimensions[0]*3:
            if x >= self.dimensions[0]:
                x = 0
                y += 1
            if solution[i] > 0:
                # Draw a balloon
                self.create_oval(
                    self.cell_width*x + 5,
                    self.cell_width*y + 5,
                    self.cell_width*(x+1) - 5,
                    self.cell_width*(y+1) - 5,
                    fill="white",
                    width=2.0
                )
            elif solution[i+1] > 0:
                # Draw a stone
                self.create_oval(
                    self.cell_width*x + 5,
                    self.cell_width*y + 5,
                    self.cell_width*(x+1) - 5,
                    self.cell_width*(y+1) - 5,
                    fill="black",
                    width=2.0
                )
            i += 3
            x += 1

    def load_grid(self, zones, blacks):
        cells = self.find_withtag("cell")

        # draw the black cells: select each cell and call toggle_selection_solid()
        for cell in blacks:
            for id in cells:
                tags = self.gettags(id)
                if ("x{}".format(cell[0]) in tags) and ("y{}".format(cell[1]) in tags):
                    self.addtag_withtag("selected", id)
        self.toggle_selection_solid()
        self.dtag("selected", "selected")

        # draw the zones: select the cells from each zone and call make_zone_from_selection()
        for zone in list(zones):
            # list() necessary because the order of the original list changes along the way:
            # this forces a copy to be made: order of the iterable isn't changed.
            for cell in zone:
                for id in cells:
                    tags = self.gettags(id)
                    if ("x{}".format(cell[0]) in tags) and ("y{}".format(cell[1]) in tags):
                        self.addtag_withtag("selected", id)
            self.make_zone_from_selection()
