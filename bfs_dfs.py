# breadth first searching
import numpy
import copy
import collections
import os
import time

# --------------------------------------------------------- #
# Since the only implementation difference between          #
# breadth first and depth first is the order in which       #
# cells are expanded, a simple boolean suffices for both    #
# -------- Comment out one of the following --------------- #

#BFS_SEARCH = False    # Depth First
BFS_SEARCH = True       # Breadth First

if BFS_SEARCH:
    TITLE = "---> BFS Search <---"
else:
    TITLE = "---> DFS Search <---"

# Pretty printing
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Used for printing 
SLEEPER = 0.00

# The moves as tuples
UP = (-1,0)
DOWN = (1,0)
LEFT = (0,-1)
RIGHT = (0,1)
Neighbours = (UP, DOWN, LEFT, RIGHT)
#-------------------#

# Cell states
START_CELL = 'P'
GOAL_CELL = '+'
WALL_CELL = '|'
SPACE_CELL = ' '
TRAVERSED_CELL = '*'

originalProblem = None
theProblem = None
GoalState = False
checkedNodes = []
expandedNodes = 0

startingNodeXY = (0,0)
goalNodeXY = (0,0)
problemWidth = 0
problemHeight = 0

startNode = None
goalNode = None

class Node:
    def __init__(self):
        self.isGoal = False
        self.frontier = []
        self.xy = [0,0]
        self.parent = None
        self.moves = collections.deque()

    def setLocation(self, yx):
        self.xy[0] = yx[0]
        self.xy[1] = yx[1]

    def populateMoves(self):
        # Loop around, checking for legal moves
        for neighbour in Neighbours:
            theCell = self.xy[0] + neighbour[0], self.xy[1] + neighbour[1]
            theCellContents = theProblem[theCell]
            if theCellContents == WALL_CELL or list(theCell) in checkedNodes:
                continue
            else:
                # Legal move found
                self.moves.append((neighbour[0],neighbour[1]))
    
    def checkGoal(self):
        global GoalState
        if theProblem[self.xy[0], self.xy[1]] == GOAL_CELL:
            global goalNode
            goalNode = self
            print "\n\nGoal Found: x-{},y-{}\n\n".format(self.xy[1], self.xy[0])
            GoalState = True
            return True
        else:
            GoalState = False
            return False

# Print the problem based on current states
def printProblem(path):
    for node in path:
        if theProblem[node[0],node[1]] == SPACE_CELL:
            theProblem[node[0],node[1]] = bcolors.FAIL + TRAVERSED_CELL + bcolors.ENDC
#    os.system('clear')
    print '\n' + TITLE
    print '\n'.join(''.join(str(cell) for cell in x) for x in theProblem)

# Print the path leading up to `node`
def printPath(node):
    while node.parent:
        if originalProblem[node.parent.xy[0],node.parent.xy[1]] == START_CELL: 
            node = node.parent
            continue
        originalProblem[node.parent.xy[0],node.parent.xy[1]] = bcolors.OKGREEN + TRAVERSED_CELL + bcolors.ENDC
        node = node.parent

        print '\n' + TITLE
        print '\n'.join(''.join(str(cell) for cell in x) for x in originalProblem)
        time.sleep(SLEEPER)

# Frontier Check
def isInFrontier(node):
    for f in frontier:
        if node.xy == f.xy:
            return True
    return False
# ---------------------  END DECLARATIONS & DEFINITIONS  ------------------- #
# -------------------------------------------------------------------------- #

with open("maze.txt", "rtU") as f:
    for line in f:
        line = line.rstrip()
        problemHeight += 1
        problemWidth = len(line.rstrip())

    # Primary data structure
    theProblem = numpy.empty((problemHeight,problemWidth), dtype=object)
    f.seek(0)
    x = 0
    y = 0

    # Populate `theProblem`
    for line in f:
        for ch in line.rstrip():
            theProblem[y,x] = ch
            if ch == START_CELL:
                startingNodeXY = (y,x)
                print "Start: {}".format(startingNodeXY)
            elif ch == GOAL_CELL:
                goalNodeXY = (y,x)
                print "Goal: {}".format(goalNodeXY)
            x += 1
        x = 0
        y += 1
    print '\n'.join(''.join(str(cell) for cell in x) for x in theProblem)


# ----------------------------------------- #
# --------- START PRIMARY LOGIC ----------- #
# ----------------------------------------- #
originalProblem = copy.deepcopy(theProblem)
startNode = Node()
goalNode = Node()

startNode.setLocation(startingNodeXY)
startNode.parent = None
goalNode.setLocation(goalNodeXY)

stateNode = copy.deepcopy(startNode)
stateNode.populateMoves()
stateNode.checkGoal()

frontier = collections.deque()
frontier.append(stateNode)

# Primary loop
while not GoalState and frontier:
    # Check search type to determine expansion order
    if BFS_SEARCH: stateNode = frontier.popleft()
    else: stateNode = frontier.pop()
    checkedNodes.append(stateNode.xy)

    while stateNode.moves and not GoalState:
        expandedNodes += 1
        if BFS_SEARCH: direction = stateNode.moves.popleft()
        else: direction = stateNode.moves.pop()
        childState = Node()
        childState.parent = stateNode

        # Set the location after the current move
        newLocation = (stateNode.xy[0] + direction[0], stateNode.xy[1] + direction[1])
        childState.setLocation(newLocation)

        if childState.xy not in checkedNodes and not isInFrontier(childState):
            if childState.checkGoal(): break
            childState.populateMoves()
            frontier.append(childState)
    printProblem(checkedNodes)
    time.sleep(SLEEPER)

# Print Results
pathCost = 1
while stateNode.parent:
    pathCost += 1
    print stateNode.parent.xy
    stateNode = stateNode.parent
printProblem(checkedNodes)
printPath(goalNode)
print "Nodes Expanded:  {}".format(expandedNodes)
print "Path Cost: {}".format(pathCost)