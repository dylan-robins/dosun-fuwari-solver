#!venv/bin/python
import pycosat as sat

def test_sat():
    mafnd = [[1, -5, 4], [-1, 5, 3, 4], [-3, -4]]
    res = sat.itersolve(mafnd)
    for x in res:
        print(x)

if __name__ == "__main__":
    test_sat()