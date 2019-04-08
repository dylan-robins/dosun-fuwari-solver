#!venv/bin/python
import itertools
import file_io as fio
import pycosat as sat


def make_each_positive_once(zone, gridWidth, mode, offset=3):
    """
    Make clauses determining the unicity of balloons or stones in a given
    zone: each cell could be a ballon/stone, but there can be two of them.
    Output is a list similar to a pycosat-compliant DIMACS list, except it's
    elements are seperated by ORs instead of ANDs.

    Arguments:
      - zone: list of cells in zone
              Format:
              [
                  [x1,y1],
                  [x2,y2],
                  [x3,y3],
                  ...
              ]
      - mode: Determines whether to make clauses for unicitiy of balloons or
              stones. 0 => balloons, 1 => stones
    """
    condition = []
    for cell in zone:
        # Variable's number is it's x index + it's y index times the width of
        # the grid + the "mode" (offset numbers by +1 if making conditions for
        # stones) + the initial numbering offset
        i = 3 * (cell[0] + cell[1] * gridWidth) + mode + offset
        condition = [i]
        for other_cell in zone:
            j = -3 * (other_cell[0] + other_cell[1] * gridWidth) + mode + offset
            if i != j:
                condition.append(j)
        yield condition


def gen_ncf(width, height, zones, blacks):
    """
    Generates the normal conjuntive form giving the satisfiability of a given
    dosun fuwari grid. Output format is a pycosat-compliant DIMACS list.

    Arguments:
        - width: width of the grid
        - height: height of the grid
        - zones: list of the zones in the grid
                 Expected format: 
                 [
                    [[x1, y1), [x2,y2], ...],
                    [[x3, y3), [x4,y4], ...], 
                    ...
                 ]
        - blacks: list of the black cells in the grid
                  Expected format:
                  [
                    [x1,y1],
                    [x2,y2],
                    ...
                  ]

    Logic rules:
        Each cell of the grid has three variables attached to it: isStone,
        isBalloon and isBlack. For a given cell (x, y) of the grid belonging
        to a given zone [[x,y], [xz1, yz1], [xz2, yz2]...], the
        rules determining whether the cell is legal are the following:
          - Each stone must be resting against a black cell or another
            stone beneath it:
                isStone(x,y) => isBlack(x, y+1) or isStone(x, y+1)
          - Each balloon must be resting against a black cell or another
            balloon above it:
                isBalloon(x,y) => isBlack(x, y-1) or isBalloon(x, y-1)
          - Each zone must have one (and only one) stone in it:
                isStone(x,y) and not isStone(xz1, yz1) and not
                isStone(xz2, yz2) and not isStone...
          - Each zone must have one (and only one) balloon in it:
                isBalloon(x,y) and not isBalloon(xz1, yz1) and not
                isBalloon(xz2, yz2) and not isBalloon...
    
    DIMACS variable naming convention:
        Variables numbers are assigned in groups of three going across each 
        row, top to bottom, starting from row -1.
        3,4,5 -> 9,10,11 and 39,40,41 -> 45,46,47 : not isBallon(0,-1) and not
        isStone(0,-1) and isBlack(0,-1) etc
		12 : (not) isBallon(0,0)
		13 : (not) isStone(0,0)
		14 : (not) isBlack(0,0)
		etc...

		    3,4,5      6,7,8   	 9,10,11 
         ________________________________
        |          |          |          |		  
        | 12,13,14 | 15,16,17 | 18,19,20 |	 
        |__________|__________|__________|
        |          |          |          |
        | 21,22,23 | 24,25,26 | 27,28,29 |	 
        |__________|__________|__________|
        |          |          |          |
        | 30,31,32 | 33,34,35 | 36,37,38 |
        |__________|__________|__________|

		  39,40,41   42,43,44  	45,46,47

    """
    ncf = []
	# Clauses for cells outside of grid (above and below)
    step = 3
    # Cells above
    for i in range(3, 3 + 3 * width - 1, step):
        ncf.append([-i])     # cells above the grid can hold a ballon
        ncf.append([-(i+1)]) # cells above the grid can hold a stone
        ncf.append([i+2])    # cells above the grid are considered black
    # Below
    for i in range(3*width*height+3*width+3, 3*width*height+3*width+3+3*width-1, step):
        ncf.append([-i])     # cells below the grid can hold a ballon
        ncf.append([-(i+1)]) # cells below the grid can hold a stone
        ncf.append([i+2])    # cells below the grid are considered black

	# Add clauses pertaining to the black cells
    i = 12
    for y in range(height):
        for x in range(width):
            if [x,y] in blacks:      # (x,y) => [x,y]
                ncf.append([i+2])    # (x,y) is black
                ncf.append([-i])     # (x,y) can't hold a balloon
                ncf.append([-(i+1)]) # (x,y) can't hold a stone
            else:
                ncf.append([-(i+2)]) # (x,y) isn't black
            i += 3

	# A cell can't simultaneously hold a balloon and a stone
    i = 3
    for i in range(3 + 3 * width, 3 * width * height + 3 * width + 3,i):
        ncf.append([-i, -(i+1)])     # not(isBalloon and isStone) = not isBalloon or not isStone

    # isStone positional conditions
    # End on row height-1 since bottom row is always resting on the bottom of
    # the grid
    i = 3 + 3 * width
    for _ in range(0, height - 1):
        for _ in range(0, width):
            # not isStone(x,y) or isStone(x,y+1) or isBlack(x,y+1)
            ncf.append([-(i+1), (i+1) + 3 * width, (i+1) + 3 * width + 1])
            i += 3  # go to next cell
    # isBalloon positional conditions
    # Start on row 1 since top row is always resting against top of grid
    i = 3 + 3 * width
    for _ in range(1, height):
        for _ in range(0, width):
            # not isBalloon(x,y) or isBalloon(x,y-1) or isBlack(x,y-1)
            ncf.append([-i, i - 3 * width, i - 3 * width + 2])
            i += 3  # go to next cell
    # Zone unicity conditions
    for zone in zones:
        # Each cell could be a balloon
        for clause in itertools.product(
            *[not_a_clause for not_a_clause in make_each_positive_once(zone, width, 0)]
        ):
            # not_a_clause is similar to a DIMACS list except it's elements are
            # seperated by ands instead of ors. We have to do distibute it's
            # terms with itertools.product in order to get clauses
            ncf.append(list(clause))
        # Each cell could be a stone
        for clause in itertools.product(
            *[not_a_clause for not_a_clause in make_each_positive_once(zone, width, 1)]
        ):
            ncf.append(list(clause))
    return ncf

if __name__ == "__main__":
    # Load a grid from a file and display it
    grid = fio.read_grid("grid_3x3.json")
    print("Grid:")
    print(grid)

    # Generate the DIMACS list associated with the grid and display the clauses
    ncf = list(gen_ncf(grid["width"], grid["height"], grid["zones"], grid["blacks"]))
    print("Clauses:")
    for clause in ncf:
        print(clause)

    # Solve the grid and display all solutions
    res = list(sat.itersolve(ncf))
    if len(res) > 0:
        print("Solutions:")
        for solution in res:
            print(solution)
    else:
        print("No solution found.")
