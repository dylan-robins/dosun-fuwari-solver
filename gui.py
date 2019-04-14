#!venv/bin/python
from tkinter import *
from tkinter.ttk import *

from grid import Grid

def quit():
    global root
    root.destroy()

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
        self.solvable = StringVar()
        self.create_widgets()
        

    def create_widgets(self):
        """ Dessine la fenêtre principale """
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
        Label(left_bar, text=self.TITLE, font=("Helvetica", 16), padding=(0, 0, 0, 10)).grid(
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

        # Ajouter une nouvelle grille
        dosun_grid = Grid(self.grid_dimensions[0], self.grid_dimensions[1], self.solvable, mid_bar)
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
        Label(right_bar, textvariable=self.solvable, font=("Helvetica", 12)).grid(
            row=3, column=0, sticky=S, pady=(10, 10)
        )
    
    def save_grid(self):
        print("Save the grid as a json file")

    def export_dimacs(self):
        print("Export the grid as a DIMACS file")

    def new_grid(self):
        self.destroy()
        self.master.change(Start_Frame, [])

    def create_menu(self, root):
        menubar = Menu(root)
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="New grid", command=self.new_grid)
        fileMenu.add_command(label="Save grid", command=self.save_grid)
        fileMenu.add_command(label="Export DIMACS", command=self.export_dimacs)
        fileMenu.add_separator()
        fileMenu.add_command(label="Quit", command=quit)
        menubar.add_cascade(label="File", menu=fileMenu)
        return menubar

class Start_Frame(Frame):
    TITLE = "Dosun Fuwari Solver"
    HELPTEXT = "Enter the dimensions of the grid you want to create: (maximum 20x20)"

    def __init__(self, master=None):
        """ Initialisation automatique à la création de la fenêtre d'initialisation """
        super().__init__(master, padding=(20, 20, 20, 20))
        self.master = master
        self.x = IntVar()
        self.x.set(2)
        self.y = IntVar()
        self.y.set(2)
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
                    return 1 <= int(value_if_allowed) <= 20
                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def start_editor(self, x, y, event=None):
        """ Lance la fenêtre principale """
        self.destroy()
        self.master.change(Editor_Frame, [x, y])

    def create_menu(self, root):
        menubar = Menu(root)
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Quit", command=quit)
        menubar.add_cascade(label="File", menu=fileMenu)
        return menubar



class Window(Tk):
    def __init__(self):
        super().__init__()

        self.frame = Start_Frame(self)

        menubar = self.frame.create_menu(self)
        self.configure(menu=menubar)
        
        self.frame.pack(fill=BOTH, expand=1)

    def change(self, frame, args=None):
        if len(args) > 0:
            self.frame = frame(*args, self)
        else:
            self.frame = frame(self)
        
        menubar = self.frame.create_menu(self)
        self.configure(menu=menubar)
        
        self.frame.pack(fill=BOTH, expand=1)  # make new frame


if __name__ == "__main__":
    # Créer une fenêtre Tk et y initialiser une fenêtre principale
    root = Window()
    root.resizable(False, False)
    root.mainloop()
