#!venv/bin/python
# importer les éléments Tk que l'on utilise pour le GUI
from tkinter import (
    Tk,
    Button,
    Label,
    Menu,
    Frame,
    Entry,
    LEFT,
    N,
    S,
    W,
    E,
    StringVar,
    IntVar,
)
from tkinter.ttk import Button, Label, Frame, Entry
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno

# Classe de la grille de Dosun Fuwari (basée sur un tkinter.Canvas)
from lib.grid import Grid
# Fonctions d'import/export de fichiers
import lib.file_io as fio
# Fonctions de résolution de grille
from lib.gen_formule import gen_cnf, sat_3sat


def quit():
    """
    Détruit l'objet principal Tk, le global root. Termine l'execution du
    programme.
    """
    global root
    root.destroy()


class Editor_Frame(Frame):
    """
    Fenêtre d'édition de grille de Dosun Fuwari. Permet de créer une nouvelle
    grille (ou d'en charger une préexistante depuis un fichier), puis de la
    résoudre avec pycosat, de l'enregistrer dans un fichier JSON, ou d'exporter
    la formule de solvabilité dans un fichier DIMACS.
    """

    # Variables de classe contenant les chaines statiques à afficher
    TITLE = "Dosun Fuwari Solver"
    HELPTEXT = (
        "Click on a cell to select it, then use the buttons below to "
        "set it to black or to create a zone from the selection."
    )

    def __init__(self, grid_w, grid_h, grid, master=None):
        """
        Initialisation automatique à la création de la fenêtre d'édition.
        Arguments:
          - grid_w: largeur de la grille
          - grid_h: hauteur de la grille
          - grid: dictionnaire contenant la liste des cases noires et la liste
                  des zones de la grille. Format: {"blacks": [], "zones": []}
          - master (optional): objet Tk parent
        """
        super().__init__(master)
        # assigner les variables d'instance
        self.master = master
        self.grid_dimensions = (grid_w, grid_h)  # dimensions de la grille
        # StringVar qui contiendra le résultat du satsolver à afficher
        self.solvable = StringVar()
        self.grid = grid

        # création des éléments à afficher
        self.create_widgets()

    def create_widgets(self):
        """
        Créé et affiche tous les éléments de la fenêtre d'édition de grille
        """
        # Créer trois conteneurs
        left_bar = Frame(self, padding=(10, 10, 10, 10))
        left_bar.columnconfigure(0, weight=1)
        left_bar.grid(row=0, column=0, sticky=N + S + W)

        mid_bar = Frame(self)
        mid_bar.columnconfigure(0, weight=1)
        mid_bar.grid(row=0, column=1, sticky=N + S + W + E)

        right_bar = Frame(self, padding=(10, 10, 10, 10))
        right_bar.columnconfigure(0, weight=1)
        right_bar.grid(row=0, column=2, sticky=N + S + W)

        # Ajouter deux zones de texte dans la barre de gauche
        # Titre principal
        Label(
            left_bar, text=self.TITLE, font=("Helvetica", 16), padding=(0, 0, 0, 10)
        ).grid(row=0, column=0, sticky=N)
        # Texte d'aide
        Label(
            left_bar,
            text=self.HELPTEXT,
            font=("Helvetica", 12),
            wraplength=250,
            anchor=N,
            justify=LEFT,
        ).grid(row=1, column=0, sticky=N)

        # Créer une nouvelle grille vide avec les bonnes dimensions
        self.dosun_grid = Grid(
            self.grid_dimensions[0],
            self.grid_dimensions[1],
            self.solvable,
            self.grid["blacks"],
            self.grid["zones"],
            master=mid_bar,
        )
        self.dosun_grid.grid(row=0, column=1, sticky=W + E + N + S)

        # Ajouter les boutons
        Button(
            right_bar,
            text="Create zone from selection",
            command=self.dosun_grid.make_zone_from_selection,
        ).grid(row=0, column=0, sticky=W + E)
        Button(
            right_bar,
            text="Make selection solid",
            command=self.dosun_grid.toggle_selection_solid,
        ).grid(row=1, column=0, sticky=W + E)
        Button(right_bar, text="Solve!", command=self.dosun_grid.solve).grid(
            row=2, column=0, sticky=W + E
        )
        # Dessiner la zone de texte associée au StringVar self.solvable
        Label(right_bar, textvariable=self.solvable, font=("Helvetica", 12)).grid(
            row=3, column=0, sticky=S, pady=(10, 10)
        )

    def save_grid(self):
        """
        Enregistre la grille au format JSON.
        """
        filename = asksaveasfilename(
            initialdir=".",
            filetypes=(("JSON File", "*.json"), ("All Files", "*.*")),
            title="Choose a file.",
        )
        if filename:
            grid = self.dosun_grid.get_grid()
            fio.save_grid(grid, filename)

    def export_dimacsSAT(self):
        """
        Exporte le fichier DIMACS associé à la grille.
        """
        filename = asksaveasfilename(
            initialdir=".",
            filetypes=(("DIMACS File", "*.cnf"), ("All Files", "*.*")),
            title="Choose a file.",
        )
        if filename:
            grid = self.dosun_grid.get_grid()
            sat = gen_cnf(grid["width"], grid["height"], grid["zones"], grid["blacks"])
            fio.save_dimacs(sat, filename)

    def export_dimacs3SAT(self):
        """
        Exporte le fichier DIMACS (réduit en 3-SAT) associé à la grille.
        """
        filename = asksaveasfilename(
            initialdir=".",
            filetypes=(("DIMACS File", "*.cnf"), ("All Files", "*.*")),
            title="Choose a file.",
        )
        if filename:
            grid = self.dosun_grid.get_grid()
            cnf = gen_cnf(grid["width"], grid["height"], grid["zones"], grid["blacks"])
            tab = sat_3sat(cnf, grid["height"], grid["width"])
            fio.save_dimacs(tab, filename)

    def new_grid(self):
        """
        Ferme la fenêtre d'édition et retourne à la fenêtre de choix de
        dimensions afin de créer une nouvelle grille.
        """
        self.destroy()
        self.master.change(Start_Frame, [])

    def open_grid(self):
        """
        Ouvre une grille depuis un fichier JSON dans une nouvelle fenêtre
        d'édition.
        """
        filename = askopenfilename(
            initialdir=".",
            filetypes=(("JSON File", "*.json"), ("All Files", "*.*")),
            title="Choose a file.",
        )
        if filename:
            grid = fio.read_grid(filename)
            self.destroy()
            self.master.change(Editor_Frame, [grid["width"], grid["height"], grid])

    def create_menu(self, root):
        """
        Dessine le "menu" - la barre d'options en haut de la fenêtre.
        """
        menubar = Menu(root)
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="New grid", command=self.new_grid)
        fileMenu.add_command(label="Open grid", command=self.open_grid)
        fileMenu.add_command(label="Save grid", command=self.save_grid)
        fileMenu.add_command(label="Export DIMACS SAT", command=self.export_dimacsSAT)
        fileMenu.add_command(label="Export DIMACS 3SAT", command=self.export_dimacs3SAT)
        fileMenu.add_separator()
        fileMenu.add_command(label="Quit", command=quit)
        menubar.add_cascade(label="File", menu=fileMenu)
        return menubar


class Start_Frame(Frame):
    """
    Fenêtre initiale. Demande à l'utilisateur d'entrer les dimensions de la
    grille à créer. Permet également d'ouvrir une grille préexistante.
    """

    TITLE = "Dosun Fuwari Solver"
    HELPTEXT = "Enter the dimensions of the grid you want to create: (maximum 20x20)"

    def __init__(self, master=None):
        """
        Initialisation automatique à la création de la fenêtre d'initialisation
        """
        super().__init__(master, padding=(20, 20, 20, 20))
        # assigner les variables d'instance
        self.master = master
        # variables Tk qui contiendront les valeurs entrées dans les deux champs de
        # texte
        self.x = IntVar()
        self.y = IntVar()
        # Les initialiser à des valeurs cohérentes
        self.x.set(2)
        self.y.set(2)

        # Dessiner la fenêtre
        self.create_widgets()

    def create_widgets(self):
        """
        Affiche le formulaire de démarrage.
        """
        # Titre
        Label(
            self,
            text=self.TITLE,
            font=("Helvetica", 16),
            anchor=N,
            padding=(0, 0, 0, 10),
        ).grid(row=0, column=0, columnspan=4, sticky=W + E + N)
        # Texte d'indication
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
        # Empêche la création de grilles de dimensions ridicules
        vcmd = (self.register(self.validate), "%d", "%P", "%S")

        # Formulaire d'entrée de la largeur de la grille
        Label(self, text="Width:").grid(row=2, column=0)
        x_entry = Entry(self, textvariable=self.x, validate="key", validatecommand=vcmd)
        x_entry.grid(row=2, column=1, sticky=W + E)
        # Formulaire d'entrée de la hauteur de la grille
        Label(self, text="Height:").grid(row=3, column=0)
        y_entry = Entry(self, textvariable=self.y, validate="key", validatecommand=vcmd)
        y_entry.grid(row=3, column=1, sticky=W + E)

        # Bouton Start
        sub_btn = Button(
            self,
            text="Start!",
            command=lambda: self.start_editor(int(x_entry.get()), int(y_entry.get())),
        )
        # Associer la même action à la touche entrée qu'au bouton start
        self.master.bind(
            "<Return>",
            lambda e: self.start_editor(int(x_entry.get()), int(y_entry.get()), e),
        )
        # Pareil avec le bouton entrée du pavé numérique
        self.master.bind(
            "<KP_Enter>",
            lambda e: self.start_editor(int(x_entry.get()), int(y_entry.get()), e),
        )
        sub_btn.grid(row=2, column=3, rowspan=2)

    def validate(self, action, value_if_allowed, text):
        """
        Renvoie True ssi la valeur fournie dans text est convertissable en
        entier et a une valeur autorisée ( > 0 et <= 20)
        Source: https://stackoverflow.com/a/31048136
        """
        # Ne vérifier l'entrée que si on insère un caractère
        if action == "1":
            # N'autoriser que des chiffres
            if text in "0123456789":
                try:
                    # Vérifier que la valeur saisie est un entier et est entre
                    # les bornes choisies
                    return 0 < int(value_if_allowed) <= 20
                except ValueError:
                    # La valeur n'était pas un entier: enpêcher la saisie
                    return False
            else:
                # La valeur n'était pas un chiffre
                return False
        else:
            # Sinon on s'en fout (on n'empêche pas de supprimer, sélectionner
            # comme on veut)
            return True

    def start_editor(self, x, y, event=None):
        """
        Détruit la fenêtre initiale et ouvre une fenêtre d'édition avec une
        grille de la taille choisie par l'utilisateur
        """
        self.destroy()
        self.master.change(Editor_Frame, [x, y, {"blacks": [], "zones": []}])

    def open_grid(self):
        """
        Ouvre une grille préexistante dans une fenêtre d'édition
        """
        filename = askopenfilename(
            initialdir=".",
            filetypes=(("JSON File", "*.json"), ("All Files", "*.*")),
            title="Choose a file.",
        )
        if filename:
            grid = fio.read_grid(filename)
            self.destroy()
            self.master.change(Editor_Frame, [grid["width"], grid["height"], grid])

    def create_menu(self, root):
        """
        Dessine le "menu" - la barre d'options en haut de la fenêtre.
        """
        menubar = Menu(root)
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Open grid", command=self.open_grid)
        fileMenu.add_command(label="Quit", command=quit)
        menubar.add_cascade(label="File", menu=fileMenu)
        return menubar


class Window(Tk):
    """
    Conteneur Tk dans lequel on dessine les différentes fenêtres
    """

    def __init__(self):
        """
        Initialisation automatique de l'instance
        """
        super().__init__()

        # cacher la fenêtre, dessiner la fenêtre et le menu, puis re-afficher
        # la fenêtre
        self.withdraw()

        # Empêcher le redimentionnement de la fenêtre
        self.resizable(False, False)

        # Charger la fenêtre initiale
        self.frame = Start_Frame(self)
        menubar = self.frame.create_menu(self)
        self.configure(menu=menubar)
        self.frame.pack(expand=1)
        self.deiconify()

    def change(self, frame, args=None):
        """
        Change la fenêtre affichée à l'écran.
        Arguments:
          - frame: classe de la fenêtre à créer
          - args: liste des arguments à fournir à la classe lors de son
                  instanciation
        """
        # cacher la fenêtre, dessiner la nouvelle fenêtre et le menu, puis
        # re-afficher la fenêtre
        self.withdraw()
        # instancier la nouvelle fenêtre avec les bons arguments
        if len(args) > 0:
            self.frame = frame(*args, master=self)
        else:
            self.frame = frame(master=self)
        menubar = self.frame.create_menu(self)
        self.configure(menu=menubar)
        self.update_idletasks()  # vérifier que la fenêtre a bien été mise à jour
        self.frame.pack(expand=1)  # dessiner la nouvelle fenêtre
        self.deiconify()


if __name__ == "__main__":
    # Créer une fenêtre Tk, la nommer et y initialiser une fenêtre principale
    root = Window()
    root.title("Dosun Fuwari Solver")
    root.mainloop()
