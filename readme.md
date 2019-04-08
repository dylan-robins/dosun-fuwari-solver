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

+ Fix `gen_ncf()`:
    + **[BUG]** Clauses contain variables numbered 0 (illegal for pycosat)  //WIP
    + **[BUG]** Line 135 is wrong: we're generating *not isBalloon AND not isStone* instead of *not isBalloon OR not isStone*   //false
+ [Feature] Merge scripts into one coherent program
+ [Feature] Add functions to export/import DIMACS files
+ [Feature] Add GUI to save/load grids/DIMACS files
+ [Feature] Undo/redo in GUI?

## Authors
+ [Dylan ROBINS](https://github.com/dylan-robins/)
+ Lucas DREZET
+ Louis WADBLED

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
