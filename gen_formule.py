#!venv/bin/python
import itertools
# import pycosat as sat


def make_each_negative_once(zone, gridWidth, mode, offset=3):
    """
    List conditions determining the unicity of balloons or stones in a given zone.

    Arguments:
      - zone: list of cells in zone
              Format:
              [
                  (x1,y1),
                  (x2,y2),
                  (x3,y3),
                  ...
              ]
      - mode: Determines whether to make clauses for unicitiy of balloons or
              stones. 0 => balloons, 1 => stones
    """
    condition = []
    for cell in zone:
        # Cell's number is it's x index + it's y index times the width of the
        # grid + the "mode" (offset numbers by 1 if making conditions for
        # stones) + the initial numbering offset
        i = 3 * (cell[0] + cell[1] * gridWidth) + mode + offset
        condition = [-i]
        for other_cell in zone:
            j = 3 * (other_cell[0] + other_cell[1] * gridWidth) + mode + offset
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
                    [(x1, y1), (x2,y2), ...],
                    [(x3, y3), (x4,y4), ...], 
                    ...
                 ]
        - blacks: list of the black cells in the grid
                  Expected format:
                  [
                    (x1,y1),
                    (x2,y2),
                    ...
                  ]

    Logic rules:
        Each cell of the grid has three variables attached to it: isStone,
        isBalloon and isBlack. For a given cell (x, y) of the grid belonging
        to a given zone [(x,y), (xz1, yz1), (xz2, yz2)...], the
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
        row, top to bottom, starting from 3 (-0 is not distinct from 0, so 
        numbers 0 through 3 can cause problems)
        So 3, 4 and 5 are respectively isBallon(), isStone() and isBlack(0,0),
        then 6 is isBallon(1,0), 7 is isStone(1,0) etc.
        Visual example:
         ________________________________
        |          |          |          |
        |  3,4,5   |  6,7,8   | 9,10,11  |
        |__________|__________|__________|
        |          |          |          |
        | 12,13,14 | 15,16,17 | 18,19,20 |
        |__________|__________|__________|
        |          |          |          |
        | 21,22,23 | 24,25,26 | 27,28,29 |
        |__________|__________|__________|
    """
    ncf = []
    # isStone positional conditions
    # End on row height-1 since bottom row is always resting on the bottom of
    # the grid
    i = 3 * width + 3
    for _ in range(0, height - 1):
        for _ in range(0, width):
            # not isStone(x,y) or isStone(x,y-1) or isBlack(x,y-1)
            ncf.append([-i, i - 3 * width, i - 3 * width + 2])
            i += 3  # go to next cell
    # isBalloon positional conditions
    # Start on row 1 since top row is always resting against top of grid
    i = 3
    for _ in range(1, height):
        for _ in range(0, width):
            # not isBalloon(x,y) or isBalloon(x,y-1) or isBlack(x,y-1)
            ncf.append([-(i + 1), i + 3 * width + 1, i + 3 * width + 2])
            i += 3  # go to next cell

    # Zone unicity conditions
    for zone in zones:
        # Each cell could be a balloon
        for clause in itertools.product(
            *[not_a_clause for not_a_clause in make_each_negative_once(zone, width, 0)]
        ):
            # not_a_clause is similar to a DIMACS list except it's elements are
            # seperated by ands instead of ors. We have to do distibute it's
            # terms with itertools.product in order to get clauses
            ncf.append(list(clause))
    return ncf


def generate_formula(width, height, zones, blacks):
    '''
    Same as gen_ncf(): generates the normal conjuntive form giving the
    satisfiability of a given dosun fuwari grid. Output format is a human
    readable logic formula.
    '''
    formula = ""
    # Pour chaque case définir si elle est noire ou non
    for y in range(height):
        for x in range(width):
            if (x,y) in blacks:
                formula += f"(N({x},{y}))"
                # une case noire ne peut pas contenir de ballon ou de pierre
                formula += f"(-B({x},{y}))(-P({x},{y}))\n"
            else:
                formula += f"(-N({x},{y}))\n"
    # Définir que chaque case ne peut contenir à la fois un ballon et une pierre
    for y in range(height):
        for x in range(width):
            formula += f"(-B({x},{y})+-P({x},{y}))\n"
    # 1e partie: pour chaque case (x,y) de la grille
    # ajouter B(x,y) => N(x,y-1) + B(x,y-1) et P(x,y) => N(x,y-1) + P(x,y-1)
    for y in range(height):
        for x in range(width):
            formula += f"(-B({x},{y})+N({x},{y-1})+B({x},{y-1}))\n"
            formula += f"(-P({x},{y})+N({x},{y+1})+P({x},{y+1}))\n"
    # 2e partie: pour chaque zone zi de la grille
    # ajouter (il existe une unique case (x,y) dans zi telle que B(x,y))
    #      et (il existe une unique case (x',y') dans zi telle que P(x',y'))
    for zone in zones:
        # Creer deux listes avec les bouts de formule à racoller
        ballons = []
        pierres = []
        for perm in itertools.permutations(zone):
            # unique (x,y) dans la zone tq B(x,y)
            new_perm = []
            new_perm.append(f"B({perm[0][0]},{perm[0][1]})")
            for i in range(1, len(perm)):
                new_perm.append(f"-B({perm[i][0]},{perm[i][1]})")
            ballons.append(tuple(new_perm))
            # unique (x',y') dans la zone tq P(x',y')
            new_perm = []
            new_perm.append(f"P({perm[0][0]},{perm[0][1]})")
            for i in range(1, len(perm)):
                new_perm.append(f"-P({perm[i][0]},{perm[i][1]})")
            pierres.append(tuple(new_perm))
        # Convertir les listes en clauses
        # Et les ajouter à la formule
        for clause in itertools.product(*ballons):
            formula += "(" + "+".join(clause) + ")\n"
        for clause in itertools.product(*pierres):
            formula += "(" + "+".join(clause) + ")\n"
    return formula


if __name__ == "__main__":
    #######################
    #     exemple 2x2     #
    #######################
    # x,y = 2,2
    # zones = [
    #     [(0,0), (0,1)],
    #     [(1,0), (1,1)],
    # ]
    # blacks = []

    #######################
    #     exemple 3x3     #
    #######################
    x, y = 3, 3
    zones = [[(0, 0), (1, 0)], [(2, 0), (2, 1), (2, 2)], [(1, 1), (1, 2), (0, 2)]]
    blacks = [(0, 1)]

    #######################
    #    exemple 10x10    #
    #######################
    # x, y = 10, 10

    # zones = [
    #     [(0, 0), (0, 1)],
    #     [(0, 3), (0, 4), (0, 5), (1, 5)],
    #     [(0, 7), (0, 8)],
    #     [(1, 9), (2, 9)],
    #     [(1, 7), (2, 7)],
    #     [(2, 8), (3, 8), (3, 9), (4, 9)],
    #     [(1, 6), (2, 6), (3, 6), (3, 7)],
    #     [(2, 4), (2, 5), (3, 5)],
    #     [(2, 2), (1, 3), (2, 3)],
    #     [(1, 1), (1, 2)],
    #     [(2, 0), (3, 0)],
    #     [(5, 0), (3, 1), (4, 1), (5, 1)],
    #     [(3, 2), (4, 2), (3, 3)],
    #     [(4, 3), (4, 4), (4, 5), (4, 6)],
    #     [(5, 7), (4, 8), (5, 8), (5, 9)],
    #     [(5, 6), (6, 6), (6, 7)],
    #     [(5, 4), (6, 4), (5, 5)],
    #     [(6, 2), (5, 3), (6, 3), (7, 3), (8, 3)],
    #     [(6, 0), (7, 0), (6, 1)],
    #     [(8, 1), (7, 2), (8, 2)],
    #     [(8, 0), (9, 0)],
    #     [(9, 2), (9, 3)],
    #     [(8, 4), (7, 5), (8, 5), (9, 5)],
    #     [(8, 6), (9, 6), (8, 7)],
    #     [(9, 7), (8, 8), (9, 8)],
    #     [(7, 8), (7, 9), (8, 9)],
    # ]

    # blacks = [
    #     (0, 2),
    #     (0, 6),
    #     (0, 9),
    #     (1, 8),
    #     (3, 4),
    #     (1, 4),
    #     (1, 0),
    #     (2, 1),
    #     (4, 0),
    #     (4, 7),
    #     (6, 8),
    #     (6, 9),
    #     (6, 5),
    #     (5, 2),
    #     (7, 1),
    #     (9, 1),
    #     (9, 4),
    #     (7, 4),
    #     (9, 9),
    #     (7, 6),
    #     (7, 7),
    # ]

    #######################
    #    exemple 20x20    #
    #######################
    # x, y = 20, 20

    # blacks = [
    #     (0, 2),
    #     (1, 2),
    #     (3, 3),
    #     (5, 1),
    #     (9, 1),
    #     (11, 2),
    #     (10, 3),
    #     (5, 3),
    #     (13, 2),
    #     (14, 1),
    #     (15, 3),
    #     (16, 4),
    #     (19, 2),
    #     (19, 5),
    #     (15, 6),
    #     (1, 4),
    #     (4, 6),
    #     (6, 4),
    #     (7, 4),
    #     (10, 7),
    #     (12, 4),
    #     (13, 4),
    #     (19, 8),
    #     (1, 9),
    #     (2, 7),
    #     (5, 7),
    #     (6, 7),
    #     (8, 7),
    #     (12, 8),
    #     (14, 8),
    #     (17, 9),
    #     (3, 9),
    #     (15, 10),
    #     (18, 11),
    #     (13, 10),
    #     (9, 9),
    #     (8, 9),
    #     (5, 10),
    #     (4, 11),
    #     (8, 11),
    #     (6, 12),
    #     (2, 12),
    #     (0, 12),
    #     (19, 13),
    #     (16, 12),
    #     (14, 13),
    #     (10, 11),
    #     (1, 14),
    #     (5, 14),
    #     (6, 14),
    #     (8, 15),
    #     (11, 13),
    #     (13, 14),
    #     (17, 14),
    #     (3, 16),
    #     (4, 16),
    #     (9, 17),
    #     (12, 16),
    #     (12, 15),
    #     (11, 17),
    #     (16, 15),
    #     (15, 16),
    #     (16, 17),
    #     (19, 18),
    #     (17, 19),
    #     (1, 17),
    #     (8, 18),
    #     (13, 18),
    #     (6, 18),
    #     (4, 18),
    # ]

    # zones = [
    #     [(0, 0), (1, 0), (0, 1)],
    #     [(2, 0), (1, 1), (2, 1)],
    #     [(3, 0), (3, 1), (2, 2), (3, 2), (0, 3), (1, 3), (2, 3)],
    #     [(4, 0), (5, 0), (4, 1), (4, 2)],
    #     [(6, 1), (7, 1), (8, 1), (5, 2), (6, 2)],
    #     [(6, 0), (7, 0), (8, 0), (9, 0)],
    #     [(10, 0), (11, 0), (11, 1)],
    #     [(10, 1), (9, 2), (10, 2)],
    #     [(8, 2), (8, 3), (9, 3)],
    #     [(7, 2), (6, 3), (7, 3)],
    #     [(5, 3)],
    #     [(12, 1), (12, 2), (11, 3), (12, 3)],
    #     [(12, 0), (13, 0), (13, 1)],
    #     [(14, 2), (13, 3), (14, 3)],
    #     [(14, 0), (15, 0), (15, 1), (15, 2)],
    #     [(16, 1), (16, 2)],
    #     [(16, 0), (17, 0), (17, 1), (17, 2), (16, 3), (17, 3)],
    #     [(19, 2)],
    #     [(18, 0), (19, 0), (18, 1), (19, 1)],
    #     [(18, 2), (18, 3), (19, 3)],
    #     [(15, 4), (17, 4), (18, 4), (19, 4), (15, 5), (16, 5), (17, 5), (18, 5)],
    #     [(0, 4), (0, 5), (1, 5), (0, 6), (1, 6), (2, 6)],
    #     [(2, 4), (3, 4), (2, 5), (3, 5), (4, 5), (3, 6)],
    #     [(4, 4), (5, 4), (5, 5), (5, 6)],
    #     [(7, 4)],
    #     [(6, 5), (7, 5), (6, 6)],
    #     [(8, 4), (9, 4), (8, 5), (9, 5), (7, 6), (8, 6)],
    #     [(10, 4), (10, 5), (9, 6), (10, 6), (11, 6)],
    #     [(13, 4)],
    #     [(12, 4)],
    #     [(11, 4), (11, 5), (12, 5), (12, 6), (11, 7), (12, 7)],
    #     [(14, 4), (13, 5), (14, 5), (13, 6), (14, 6), (13, 7), (14, 7), (15, 7)],
    #     [(16, 6), (17, 6), (18, 6), (19, 6), (17, 7), (18, 7), (19, 7)],
    #     [(16, 7), (16, 8), (17, 8), (18, 8)],
    #     [(0, 7), (1, 7), (0, 8), (1, 8), (0, 9)],
    #     [(3, 7), (4, 7), (2, 8), (3, 8), (4, 8), (2, 9)],
    #     [(5, 8), (4, 9), (5, 9)],
    #     [(7, 7), (6, 8), (7, 8), (8, 8), (6, 9), (6, 10)],
    #     [(9, 7), (9, 8), (10, 8), (11, 8), (10, 9)],
    #     [(13, 8), (15, 8), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9)],
    #     [(16, 9), (18, 9), (19, 9), (16, 10), (17, 10), (18, 10), (19, 10)],
    #     [(0, 10), (1, 10), (2, 10), (0, 11)],
    #     [(3, 10), (4, 10), (1, 11), (2, 11), (3, 11)],
    #     [(7, 9), (7, 10), (5, 11), (6, 11), (7, 11)],
    #     [(8, 10), (9, 10), (10, 10), (11, 10), (12, 10)],
    #     [(17, 11), (19, 11), (17, 12), (18, 12), (19, 12)],
    #     [(14, 10), (14, 11), (15, 11), (16, 11)],
    #     [(13, 11), (13, 12), (14, 12), (15, 12)],
    #     [(9, 11), (11, 11), (12, 11), (9, 12), (10, 12), (11, 12), (12, 12)],
    #     [(1, 12), (3, 12), (0, 13), (1, 13), (2, 13), (3, 13), (0, 14)],
    #     [(4, 12), (5, 12), (4, 13), (5, 13), (4, 14)],
    #     [(7, 12), (6, 13), (7, 13)],
    #     [(8, 12), (8, 13), (9, 13), (7, 14), (8, 14), (9, 14)],
    #     [(10, 13), (12, 13), (13, 13), (10, 14), (11, 14), (12, 14)],
    #     [(15, 13), (16, 13), (14, 14), (15, 14), (16, 14)],
    #     [(17, 13), (18, 13), (18, 14), (19, 14)],
    #     [(2, 14), (3, 14), (0, 15), (1, 15), (2, 15), (3, 15)],
    #     [(4, 15), (5, 15), (6, 15), (7, 15)],
    #     [(9, 15), (7, 16), (8, 16), (9, 16)],
    #     [(12, 15)],
    #     [(10, 15), (11, 15), (10, 16), (11, 16)],
    #     [(13, 15), (13, 16), (12, 17), (13, 17)],
    #     [(14, 15), (15, 15), (14, 16)],
    #     [(17, 15), (16, 16), (17, 16), (18, 16)],
    #     [(18, 15), (19, 15), (19, 16), (19, 17)],
    #     [(17, 17), (18, 17), (16, 18), (17, 18), (18, 18)],
    #     [(18, 19), (19, 19)],
    #     [(14, 17), (15, 17), (15, 18), (15, 19), (16, 19)],
    #     [(0, 16), (1, 16), (2, 16), (0, 17)],
    #     [(5, 16), (2, 17), (3, 17), (4, 17), (5, 17)],
    #     [(6, 16), (6, 17), (7, 17), (8, 17), (7, 18)],
    #     [(14, 18), (12, 19), (13, 19), (14, 19)],
    #     [(10, 17), (10, 18), (11, 18), (12, 18), (10, 19), (11, 19)],
    #     [(9, 18), (8, 19), (9, 19)],
    #     [(0, 18), (1, 18), (2, 18), (0, 19)],
    #     [(3, 18), (1, 19), (2, 19), (3, 19)],
    #     [(5, 18), (4, 19), (5, 19)],
    #     [(6, 19), (7, 19)],
    # ]

    print(generate_formula(x, y, zones, blacks))

    # for clause in gen_ncf(x,y, zones, blacks):
    #     print(clause)

    # clauses = gen_ncf(x, y, zones, blacks)
    # res = sat.itersolve(clauses)
    # for solution in res:
    #     print(solution)
