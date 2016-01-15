# breadth first searching
import numpy
import copy
import collections
import os
import time
import math
import heapq

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
SLEEPER = 0.07

# The moves as tuples
UP = (-1,0)
DOWN = (1,0)
LEFT = (0,-1)
RIGHT = (0,1)
AVAILABLE_MOVES = (UP, DOWN, LEFT, RIGHT)
#-------------------#

# Cell states
START_CELL = 'P'
GOAL_CELL = '+'
WALL_CELL = '|'
SPACE_CELL = ' '
TRAVERSED_CELL = '*'

THE_PROBLEM = None
GOAL_STATE = False
CHECKED_NODES = []
EXPANDED_NODES = 0

startingNodeXY = (0,0)
goalNodeXY = (0,0)
problemWidth = 0
problemHeight = 0

startNode = None
goalNode = None

class Node:
    def __init__(self):
        self.isGoal = False
        self.theFrontier = []
        self.xy = [0,0]
        self.parent = None
        self.moves = []
        self.heuristic = None
        self.costFromStart = 0

    def setLocation(self, yx):
        self.xy[0] = yx[0]
        self.xy[1] = yx[1]
        self.setHeuristic()

    def setParent(self, parent):
        self.parent = parent
        self.costFromStart = parent.costFromStart+1

    def populateMoves(self):
        # Loop around, checking for legal moves
        for move in AVAILABLE_MOVES:
            theCell = self.xy[0] + move[0], self.xy[1] + move[1]
            if THE_PROBLEM[theCell] == WALL_CELL or list(theCell) in CHECKED_NODES:
                continue
            else:
                # Legal move found
                heapq.heappush(self.moves, (self.getHeuristic(theCell), move))

    def setHeuristic(self):
        self.heuristic = self.getHeuristic((self.xy[0], self.xy[1]))

    def getHeuristic(self, xy):
        # Manhattan Distance + Known Cost
        return abs(goalNodeXY[1] - self.xy[1]) + abs(goalNodeXY[0] - self.xy[0]) + self.costFromStart
        #return math.hypot(xy[1]-goalNodeXY[1],xy[0]-goalNodeXY[0]) + self.costFromStart

    def checkGoal(self):
        global GOAL_STATE
        if THE_PROBLEM[self.xy[0], self.xy[1]] == GOAL_CELL:
            global goalNode
            goalNode = self
            GOAL_STATE = True
            return True
        else:
            GOAL_STATE = False
            return False

# Print the problem based on current states
def printProblem(path):
    for node in path:
        if THE_PROBLEM[node[0],node[1]] == SPACE_CELL:
            THE_PROBLEM[node[0],node[1]] = bcolors.FAIL + TRAVERSED_CELL + bcolors.ENDC
    #os.system('clear')
    print '\n'.join(''.join(str(cell) for cell in x) for x in THE_PROBLEM)

# Print the path leading up to `node`
def printPath(node):
    while node.parent:
        if THE_PROBLEM[node.parent.xy[0],node.parent.xy[1]] == START_CELL: 
            node = node.parent
            continue
        THE_PROBLEM[node.parent.xy[0],node.parent.xy[1]] = bcolors.OKGREEN + TRAVERSED_CELL + bcolors.ENDC
        node = node.parent
        time.sleep(SLEEPER)
        print '\n'
        print '\n'.join(''.join(str(cell) for cell in x) for x in THE_PROBLEM)

# Frontier Check
def isInFrontier(node):
    for f in theFrontier:
        if node.xy == f[1].xy:
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
    THE_PROBLEM = numpy.empty((problemHeight,problemWidth), dtype=object)
    f.seek(0)
    x = 0
    y = 0

    # Populate `theProblem`
    for line in f:
        for ch in line.rstrip():
            THE_PROBLEM[y,x] = ch
            if ch == START_CELL:
                startingNodeXY = (y,x)
                print "Start: {}".format(startingNodeXY)
            elif ch == GOAL_CELL:
                goalNodeXY = (y,x)
                print "Goal: {}".format(goalNodeXY)
            x += 1
        x = 0
        y += 1

    # Starting state
    print '\n'.join(''.join(str(cell) for cell in x) for x in THE_PROBLEM)

# ----------------------------------------- #
# --------- START PRIMARY LOGIC ----------- #
# ----------------------------------------- #
startNode = Node()
startNode.setLocation(startingNodeXY)

goalNode = Node()
goalNode.setLocation(goalNodeXY)

stateNode = copy.deepcopy(startNode)
stateNode.populateMoves()
stateNode.checkGoal()

theFrontier = []
heapq.heappush(theFrontier, (stateNode.heuristic, stateNode)) #populate frontier with 'start copy' as only available Node

while not GOAL_STATE and theFrontier:
    stateNode = heapq.heappop(theFrontier)[1] #heappop returns tuple of (weighted-idx, data)
    print "Popped: {}".format(stateNode.xy)
    CHECKED_NODES.append(stateNode.xy)
    while stateNode.moves and not GOAL_STATE:
        EXPANDED_NODES += 1
        moveDirection = heapq.heappop(stateNode.moves)[1]

        nextNode = Node()
        nextNode.setParent(stateNode)
        nextNode.setLocation((stateNode.xy[0] + moveDirection[0], stateNode.xy[1] + moveDirection[1]))
        if nextNode.xy not in CHECKED_NODES and not isInFrontier(nextNode):
            if nextNode.checkGoal(): break
            nextNode.populateMoves()
            # Push to `theFrontier` with heuristic as weight
            heapq.heappush(theFrontier, (nextNode.heuristic,nextNode))
            CHECKED_NODES.append(nextNode.xy)
    
    #pretty print
    printProblem(CHECKED_NODES)
    print '*' * 50
    time.sleep(SLEEPER)

# Print Final Results
print goalNode.xy
printProblem(CHECKED_NODES)
printPath(goalNode)
print "Nodes Expanded:  {}".format(EXPANDED_NODES)
print "Path Cost: {}".format(goalNode.costFromStart)