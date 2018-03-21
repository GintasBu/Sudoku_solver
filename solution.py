assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag1=[rows[i]+cols[i] for i in range(len(rows))]
diag2=[rows[8-i]+cols[i] for i in range(len(rows))]   
unitlist = row_units + column_units + square_units+[diag1+diag2]

def assign_value(values, box, value):

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):

    boxes = cross(rows, cols)
    doubles=[box for box in boxes if len(values[box])==2]
    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    twins=[]
    for x in doubles:
        for y in doubles:
            if x<y:
                if values[x]==values[y]:
                    if x[1]==y[1]:   # twins in the same column
                        twins.append((x,y, column_units[int(x[1])-1]))
                    if x[0]==y[0]:  # twins in the same row
                        twins.append((x,y, row_units[ord(x[0])-65]))
                    a=[units for units in square_units if x in units and y in units]
                    if len(a)>0:    # twins in the same square
                        twins.append((x,y, a[0]))
                
    #should diagonal be added? seems to past all tests without NT in diagonal
    while len(twins)>0:
        toclean=twins.pop(0)

        x=toclean[0]
        y=toclean[1]
        boxes=toclean[2]
        boxes.remove(y)
        boxes.remove(x)
        for box in boxes:
            for i in range(2):
                if values[x][i] in values[box]:
                    assign_value(values, box, values[box].replace(values[x][i],''))
                    #values[box]=values[box].replace(values[x][i],'')
    return values


def grid_values(grid):
    D={}

    for r in rows:
        for t in cols:
            if grid[0]=='.':
                D[r+t]='123456789'
            else: D[r+t]=grid[0]
            grid=grid[1:]
    return D

def display(values):

    if values ==False:
        print('no Dict')
        return
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    if values:  # chechs if False was passed from one of recursive legs while tree-searching

        for k,v in values.items():
            if len(v)==1:
                list_keys=set(next(c for c in square_units if k in c)+next(c for c in column_units if k in c)+next(c for c in row_units if k in c))
                if k in diag1: 
                    list_keys=list_keys|set(diag1)
                if k in diag2: 
                    list_keys=list_keys|set(diag2)    
                list_keys.remove(k)
                
                for key in list(list_keys):
                    assign_value(values, key, values[key].replace(v,''))
                    #values[key]=values[key].replace(v,'')
        if len([box for box in values.keys() if len(values[box]) == 0]):  # during eliminate can generate an empty cell. that gives wrong solution, need to use another branch of the tree in DFS 
            return False
        else: return values
    else: return False

    

def only_choice(values):   # from classroom, my was slower
    unitlist = row_units + column_units + square_units+[diag1+diag2]
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
                #values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # elimination strategy
        values=eliminate(values)
        if not values:
            break
            return False
        #only-choice strategy
        values=only_choice(values)
        # check if improved, if not stalled=True
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after

    return values



def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    values=reduce_puzzle(values)
    if not values:
   
        return False
    else:
        if all(len(values[s])==1 for s in boxes):
            return values #'solved!!!'
    # Choose one of the unfilled squares with the fewest possibilities
        else:
            i, possible_branch=min((len(values[box]), box) for box in values.keys() if len(values[box])>1)
 
            for x in range(i):
                new_sudoku=values.copy()

                new_sudoku[possible_branch]=new_sudoku[possible_branch][x]
                attempt=search(new_sudoku)

                if attempt:
                    return attempt


def solve(grid):

    values=grid_values(grid)
    stalled=False
    while not stalled:
        #Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values=search(values)

        if all(len(values[s])==1 for s in boxes):
            return values #'solved!!!' 
            break
        values=naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    #grid='......8.68.........7..863.....8............8..8.5.9...1.8..............8.....8.4.'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        #visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
