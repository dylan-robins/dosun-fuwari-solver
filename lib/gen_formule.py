#!venv/bin/python
import itertools
import pycosat as sat

import lib.file_io as fio

def sat_3sat(cnf, height, width):
    tab = []
    i = 1 + 3 * (height + 2) * width    #determines the first index we can add in DIMACS
    for clauses in cnf:
        if len(clauses) == 1:
            tab.append([clauses[0], i, i+1])
            tab.append([clauses[0], i, -(i+1)])
            tab.append([clauses[0], -i, i+1])
            tab.append([clauses[0], -i, -(i+1)])
            i += 2
        elif len(clauses) == 2:
            tab.append([clauses[0], clauses[1], i])
            tab.append([clauses[0], clauses[1], -i])
            i += 1
        elif len(clauses) == 3:
            tab.append(clauses)
        else:
            tab.append([clauses[0], clauses[1], i])
            for k in range(1, len(clauses) - 3):
                tab.append([-i, clauses[k+1], i+1])
                i += 1
            tab.append([-i, clauses[len(clauses) - 2], clauses[len(clauses) - 1]])
    return tab    

def make_each_positive_once(zone, gridWidth, mode):
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
    for i in range(len(zone)):
	### Function to calculate the index of each cell in function of its x, y index and mode :
        j = 3 * gridWidth * (1 + zone[i][1]) + 1 + 3 * zone[i][0] + mode
	###
        condition.append(j)
    yield condition
    #negation
    for i in range(len(zone)-1):
        l = 3 * gridWidth * (1 + zone[i][1]) + 1 + 3 * zone[i][0] + mode
        for k in range(i+1, len(zone)):
            condition = []
            j = 3 * gridWidth * (1 + zone[k][1]) + 1 + 3 * zone[k][0] + mode
            condition.append(-l)
            condition.append(-j)
            yield condition


def gen_cnf(width, height, zones, blacks):
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
        row, top to bottom, starting from row -1. Example:

	        1,2,3      4,5,6     7,8,9 
         ________________________________
        |          |          |          |  In this case, 45 : isBlack(3,4)
        | 10,11,12 | 13,14,15 | 16,17,18 |                10 : isBallon(0,0)
        |__________|__________|__________|                11 : isStone(0,0)
        |          |          |          |                1  : isBallon(0,-1)
        | 19,20,21 | 22,23,24 | 25,26,27 |                12 : isBlack(0,0)
        |__________|__________|__________| 
        |          |          |          | 
        | 28,29,30 | 31,32,33 | 34,35,36 | 
        |__________|__________|__________| 

	      37,38,39   40,41,42   43,44,45

    """
    cnf = []
	# Clauses for cells outside of grid (above and below)
    step = 3
    # Cells above
    for i in range(1, 1 + 3 * width - 1, step):
        cnf.append([-i])     # cells above the grid can hold a ballon
        cnf.append([-(i+1)]) # cells above the grid can hold a stone
        cnf.append([i+2])    # cells above the grid are considered black
    # Below
    for i in range(3*width*height+3*width+1, 3*width*height+3*width+1+3*width-1, step):
        cnf.append([-i])     # cells below the grid can hold a ballon
        cnf.append([-(i+1)]) # cells below the grid can hold a stone
        cnf.append([i+2])    # cells below the grid are considered black

	# Add clauses pertaining to the black cells
    i = 1 + 3 * width
    for y in range(height):
        for x in range(width):
            if [x,y] in blacks:
                cnf.append([i+2])    # (x,y) is black
                cnf.append([-i])     # (x,y) can't hold a balloon
                cnf.append([-(i+1)]) # (x,y) can't hold a stone
            else:
                cnf.append([-(i+2)]) # (x,y) isn't black
            i += 3

	# A cell can't simultaneously hold a balloon and a stone
    for i in range(1 + 3 * width, 3 * width * height + 3 * width + 1,3):
        cnf.append([-i, -(i+1)])     # not(isBalloon and isStone) = not isBalloon or not isStone

    # isStone positional conditions
    # End on row height-1 since bottom row is always resting on the bottom of
    # the grid
    i = 1 + 3 * width
    for _ in range(0, height - 1):
        for _ in range(0, width):
            # not isStone(x,y) or isStone(x,y+1) or isBlack(x,y+1)
            cnf.append([-(i+1), (i+1) + 3 * width, (i+1) + 3 * width + 1])
            i += 3  # go to next cell
    # isBalloon positional conditions
    # Start on row 1 since top row is always resting against top of grid
    i = 1 + 3 * width * 2
    for _ in range(0, height - 1):	#I changed i and 1st for because otherwise it creates conditions for the top of the grid but not for the bot of it and it's not what we wanted. Now, it create for the bot but not for the top
        for _ in range(0, width):
            # not isBalloon(x,y) or isBalloon(x,y-1) or isBlack(x,y-1)
            cnf.append([-i, i - 3 * width, i - 3 * width + 2])
            i += 3  # go to next cell
    # Zone unicity conditions
    for zone in zones:
        # Each cell could be a balloon
        for clause in (make_each_positive_once(zone, width, 0)):
            cnf.append(list(clause))
	# Each cell could be a stone
        for clause in (make_each_positive_once(zone, width, 1)):
            cnf.append(list(clause))
    return cnf