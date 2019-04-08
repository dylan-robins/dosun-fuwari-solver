import json

def save_grid(grid, path):
    """
    Saves a grid to a file, 
    """
    with open(path, "w") as in_file:
        in_file.write(json.dumps(grid))

def read_grid(path):
    with open(path, "r") as in_file:
        grid = json.loads(in_file.read())
    return grid

if __name__ == "__main__":
    grid = {
        'width': 3,
        'height': 3,
        'zones': [
            [(0,0),(1,0)],
            [(1,1),(0,1),(1,2)],
            [(2,0),(2,1),(2,2)]
        ],
        'blacks': [
            (0,1)
        ]
    }
    save_grid(grid, "grid_3x3.json")
    contents = read_grid("grid_3x3.json")
    
    print("input:", grid)
    print("output:", contents)