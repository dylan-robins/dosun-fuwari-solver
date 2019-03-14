#!venv/bin/python
from tkinter import *
from tkinter.ttk import *


class Grid(Canvas):
    cell_width = 50
    border_width = 4

    def __init__(self, x, y, master=None):
        """ Initialisation automatique à la création d'une grille
            Prend en argument les dimensions x, y voulues de la grille """
        self.master = master
        self.dimensions = (x, y)
        self.black_cells = []
        self.zones = []
        # Initialiser le canvas
        super().__init__(
            master,
            width=x * self.cell_width + self.border_width,
            height=y * self.cell_width + self.border_width,
        )
        # Initialiser la grille
        self.draw()

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
        # Assigner à chaque cellule l'action add_selected_tag
        self.tag_bind("cell", "<ButtonPress-1>", self.add_selected_tag)

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

    def add_selected_tag(self, event):
        """ Ajoute l'élement cliqué à la sélection, ou vide la sélection 
            pour en créer une nouvelle avec juste l'élement cliqué """
        # Désélectionner l'élément cliqué
        tags = self.gettags("current")
        if "selected" in tags:
            self.dtag("current", "selected")
            if ("solid" in tags):
                self.itemconfig("current", fill="#000000")
            else:
                self.itemconfig("current", fill="#ffffff")

        # Créer une sélection à partir de l'élement cliqué
        else:
            # Trouver ses coordonnées
            x = int(tags[1][1:])
            y = int(tags[2][1:])
            # Trouver si un de ses voisins est sélectionné
            neighbours = self.find_neighbours(x, y)
            has_neighbour = False
            for cell in neighbours:
                if "selected" in self.gettags(neighbours[cell]):
                    has_neighbour = True
                    break
            # S'il n'y a pas de voisins sélectionnés, vider la sélection
            if not has_neighbour:
                self.itemconfig("selected", fill="#ffffff")
                self.itemconfig("solid", fill="#000000")
                self.dtag("selected", "selected")
            # Ajouter la cellule sélectionnée à la (nouvelle) sélection
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
                self.black_cells.remove(tuple([x, y]))
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
                if (x, y) in zone:
                    zone.remove((x,y))
            # L'ajouter à la nouvelle zone
            self.zones[-1].append((x, y))
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
                self.black_cells.remove((int(tags[1][1:]), int(tags[2][1:])))
                self.dtag(cell, "solid")
                self.itemconfig(cell, fill="#ffffff")
            else:
                self.black_cells.append((int(tags[1][1:]), int(tags[2][1:])))
                self.addtag_withtag("solid", cell)
                self.itemconfig(cell, fill="#000000")
        self.dtag("selected", "selected")

    def solve(self):
        """ Convertit la grille en une liste au format DIMACS """
        # TODO
        print(self.black_cells)
        print(self.zones)


class Editor_Frame(Frame):
    # Variables de classe contenant les chaines statiques à afficher
    TITLE = "Dosun Fuwari Solver"
    HELPTEXT = (
        "Click on a cell to select it, then use the buttons below to "
        "set it to black or to create a zone from the selection."
    )

    def __init__(self, grid_w, grid_h, master=None):
        """ Initialisation automatique à la création de la fenêtre principale """
        super().__init__(master)
        self.master = master
        self.grid_dimensions = (grid_w, grid_h)
        self.grid(row=0, column=0)
        self.create_widgets()

    def create_widgets(self):
        """ Dessine la fenêtre principale """
        # Créer trois conteneurs
        left_bar = Frame(padding=(10, 10, 10, 10))
        left_bar.grid(row=0, column=0, sticky=N + S + W + E)

        mid_bar = Frame()
        mid_bar.grid(row=0, column=1, sticky=N + S + W + E)

        right_bar = Frame(padding=(10, 10, 10, 10))
        right_bar.grid(row=0, column=2, sticky=N + S + W + E)

        # Ajouter deux zones de texte dans la barre de gauche
        Label(left_bar, text=self.TITLE, font=("Helvetica", 16)).grid(
            row=0, column=0, sticky=N
        )

        Label(
            left_bar,
            text=self.HELPTEXT,
            font=("Helvetica", 12),
            wraplength=250,
            anchor=N,
            justify=LEFT,
        ).grid(row=1, column=0, sticky=N)

        mid_bar = Frame()
        mid_bar.grid(row=0, column=1, sticky=N + S + W + E)
        # Ajouter une nouvelle grille
        dosun_grid = Grid(self.grid_dimensions[0], self.grid_dimensions[1], mid_bar)
        dosun_grid.grid(row=0, column=1, sticky=W + E + N + S)

        # Ajouter boutons
        Button(
            right_bar, text="Create zone from selection", command=dosun_grid.make_zone_from_selection
        ).grid(row=0, column=0, sticky=W + E)
        Button(
            right_bar, text="Make selection solid", command=dosun_grid.toggle_selection_solid
        ).grid(row=1, column=0, sticky=W + E)
        Button(right_bar, text="Solve!", command=dosun_grid.solve).grid(
            row=2, column=0, sticky=W + E
        )


class Start_Frame(Frame):
    TITLE = "Dosun Fuwari Solver"
    HELPTEXT = "Enter the dimensions of the grid you want to create: (maximum 20x20)"

    def __init__(self, master=None):
        """ Initialisation automatique à la création de la fenêtre d'initialisation """
        super().__init__(master, padding=(20, 20, 20, 20))
        self.master = master
        self.x = IntVar()
        self.y = IntVar()
        self.create_widgets()

    def create_widgets(self):
        """ Affiche le formulaire de démarrage """
        Label(
            self,
            text=self.TITLE,
            font=("Helvetica", 16),
            anchor=N,
            padding=(0, 0, 0, 10),
        ).grid(row=0, column=0, columnspan=4, sticky=W + E + N)
        Label(
            self,
            text=self.HELPTEXT,
            wraplength=300,
            font=("Helvetica", 12),
            anchor=N,
            justify=LEFT,
            padding=(0, 0, 0, 10),
        ).grid(row=1, column=0, columnspan=3, sticky=W + E)

        # Commande de validation des entrées
        # Source: https://stackoverflow.com/a/31048136
        vcmd = (self.register(self.validate), "%d", "%P", "%S")

        Label(self, text="Width:").grid(row=2, column=0)

        x_entry = Entry(self, textvariable=self.x, validate="key", validatecommand=vcmd)
        x_entry.grid(row=2, column=1, sticky=W + E)

        Label(self, text="Height:").grid(row=3, column=0)

        y_entry = Entry(self, textvariable=self.y, validate="key", validatecommand=vcmd)
        y_entry.grid(row=3, column=1, sticky=W + E)

        sub_btn = Button(
            self,
            text="Start!",
            command=lambda: self.start_editor(int(x_entry.get()), int(y_entry.get())),
        )
        self.master.bind('<Return>', lambda e: self.start_editor(int(x_entry.get()), int(y_entry.get()), e))
        sub_btn.grid(row=2, column=3, rowspan=2)

    def validate(self, action, value_if_allowed, text):
        ''' Renvoie True ssi la valeur fournie dans text est 
            convertissable en entier.
            Source: https://stackoverflow.com/a/31048136 '''
        if action == "1":
            if text in "0123456789":
                try:
                    return int(value_if_allowed) <= 20
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def start_editor(self, x, y, event=None):
        """ Lance la fenêtre principale """
        self.grid_forget()
        self.master.change(Editor_Frame, [x, y])


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.frame = Start_Frame(self)
        self.frame.grid()

    def change(self, frame, args=None):
        self.frame.pack_forget()  # delete currrent frame
        if len(args) != 0:
            self.frame = frame(*args, self)
        else:
            self.frame = frame(self)
        self.frame.grid()  # make new frame


if __name__ == "__main__":
    # Créer une fenêtre Tk et y initialiser une fenêtre principale
    root = Window()
    root.mainloop()
