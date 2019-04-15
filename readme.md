# Dosun Fuwari Solver

A python program that solves dosun fuwari grids for you.

## Dependencies

To run this program you'll need to install the following programs:
+ Python 3.6
+ Tkinter
+ Pycosat

## Program structure

The solver is currently split in three parts: `gui.py` is the graphical grid creation tool, `gen_formule.py` is the core logic and `file_io.py` contains the functions used for importing/exporting grids to and from files.

## To do

+ [Test] Test fucntion `SAT to 3-SAT`: problem when use pycosat (endless loop), don't have a problem with minisat when export with save_dimacs
+ [Feature] Add function to import DIMACS files
+ [Feature] Add `Grid` class method to open an existing grid
+ [Feature] [Optional] Undo/redo in GUI?

## Authors
+ [Dylan ROBINS](https://github.com/dylan-robins/)
+ Lucas DREZET
+ Louis WADBLED

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
