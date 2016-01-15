# breadth first searching
import numpy
import copy
import collections
import os
import time
import math
import heapq

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SLEEPER = .08

# The moves as tuples
UP = (-1,0)
DOWN = (1,0)
LEFT = (0,-1)
RIGHT = (0,1)
Neighbours = (UP, DOWN, LEFT, RIGHT)
#-------------------#

originalProblem = None
theProblem = None
GoalState = False
checkedNodes = []
expandedNodes = 0

startingNodeXY = (0,0)
goalNodeXY = (0,0)
width = 0
height = 0

startNode = None
goalNode = None

class Node:
    def __init__(self):
        self.isGoal = False
        self.frontier = []
        self.xy = [0,0]
        self.parent = None
        self.moves = []
        self.heuristic = None

    def setLocation(self, yx):
        self.xy[0] = yx[0]
        self.xy[1] = yx[1]
        self.setHeuristic()

    def populateMoves(self):
        for neighbour in Neighbours:
            theCell = self.xy[0] + neighbour[0], self.xy[1] + neighbour[1]
            theCellContents = theProblem[theCell]
            if theCellContents == '|' or list(theCell) in checkedNodes:
                continue
            else:
                heapq.heappush(self.moves, (getHeuristic(neighbour),neighbour))
    
    def checkGoal(self):
        global GoalState
        if theProblem[self.xy[0], self.xy[1]] == '+':
            global goalNode
            goalNode = self
            print "\n\nGoal Found: x-{},y-{}\n\n".format(self.xy[1], self.xy[0])
            GoalState = True
            return True
        else:
            GoalState = False
            return False

    def setHeuristic(self):
        #self.heuristic = math.hypot(self.xy[1]-goalNodeXY[1],self.xy[0]-goalNodeXY[0])
        self.heuristic = abs(goalNodeXY[1] - self.xy[1]) + abs(goalNodeXY[0] - self.xy[0])  # Manhattan Distance
        #self.heuristic = max(abs(goalNodeXY[1] - self.xy[1]) + abs(goalNodeXY[0] - self.xy[0]), math.hypot(self.xy[1]-goalNodeXY[1],self.xy[0]-goalNodeXY[0]))


def getHeuristic(xy):
    #return math.hypot(xy[1]-goalNodeXY[1],xy[0]-goalNodeXY[0])
    return abs(goalNodeXY[1] - xy[1]) + abs(goalNodeXY[0] - xy[0])
    #return max(abs(goalNodeXY[1] - xy[1]) + abs(goalNodeXY[0] - xy[0]), math.hypot(xy[1]-goalNodeXY[1],xy[0]-goalNodeXY[0]))


def printProblem(path):
    for node in path:
        if theProblem[node[0],node[1]] == ' ':
            theProblem[node[0],node[1]] = bcolors.FAIL + '*' + bcolors.ENDC
    #os.system('clear')
    print '\n'
    print '\n'.join(''.join(str(cell) for cell in x) for x in theProblem)

def printPath(node):
    while node.parent:
        if theProblem[node.parent.xy[0],node.parent.xy[1]] == 'P': 
            node = node.parent
            continue
        theProblem[node.parent.xy[0],node.parent.xy[1]] = bcolors.OKGREEN + '*' + bcolors.ENDC
        node = node.parent
        print '\n'
        print '\n'.join(''.join(str(cell) for cell in x) for x in theProblem)
        time.sleep(SLEEPER)

def isInFrontier(node):
    for f in frontier:
        if node.xy == f[1].xy:
            return True
    return False
# ---------------------  END DECLARATIONS & DEFINITIONS  ------------------- #
# -------------------------------------------------------------------------- #

with open("maze.txt", "rtU") as f:
    for line in f:
        line = line.rstrip()
        height += 1
        width = len(line.rstrip())

     # Primary data structure
    theProblem = numpy.empty((height,width), dtype=object)
    f.seek(0)
    x = 0
    y = 0

    # Populate `theProblem`
    for line in f:
        for ch in line.rstrip():
            theProblem[y,x] = ch
            if ch == 'P':
                startingNodeXY = (y,x)
                print "Start: {}".format(startingNodeXY)
            elif ch == '+':
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
print "Current Location: {}".format(stateNode.xy)
stateNode.populateMoves()
stateNode.checkGoal()
frontier = []
heapq.heappush(frontier, (stateNode.heuristic, stateNode))

while not GoalState and frontier:
    stateNode = heapq.heappop(frontier)[1]
    checkedNodes.append(stateNode.xy)
    
    while stateNode.moves and not GoalState:
        expandedNodes += 1
        direction = heapq.heappop(stateNode.moves)[1]
        childState = Node()
        childState.parent = stateNode
        newLocation = (stateNode.xy[0] + direction[0], stateNode.xy[1] + direction[1])
        childState.setLocation(newLocation)
        if childState.xy not in checkedNodes and not isInFrontier(childState):
            if childState.checkGoal(): break
            childState.populateMoves()
            heapq.heappush(frontier, (childState.heuristic,childState))
            checkedNodes.append(childState.xy)
    printProblem(checkedNodes)
    time.sleep(SLEEPER)


pathCost = 1
while stateNode.parent:
    pathCost += 1
    print stateNode.parent.xy
    stateNode = stateNode.parent

printProblem(checkedNodes)
printPath(goalNode)
print "Nodes Expanded:  {}".format(expandedNodes)
print "Path Cost: {}".format(pathCost)