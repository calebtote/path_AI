# breadth first searching
import numpy
import copy
import collections
import os
import time
import math
import heapq

#for pretty printing
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
SLEEPER = 0.01

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
goalNodesXY = []
weightedPath = []

currentGoalNodesXY = []
currentGoalXY = (0,0)
weightedGoalNodes = []
currentGoalFound = False
currentStartingNodeXY = (0,0)

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
        for move in AVAILABLE_MOVES:
            theCell = self.xy[0] + move[0], self.xy[1] + move[1]
            if THE_PROBLEM[theCell] == WALL_CELL or list(theCell) in CHECKED_NODES:
                continue
            else:
                heapq.heappush(self.moves, (self.getHeuristic(theCell), move))

    def setHeuristic(self):
        self.rebuildCost()
        self.heuristic = self.getHeuristic((self.xy[0], self.xy[1]))

    def getHeuristic(self, xy):
        # Same A* Heuristic
        return abs(currentGoalXY[1] - self.xy[1]) + abs(currentGoalXY[0] - self.xy[0]) + self.costFromStart

    def checkGoal(self):
        global currentGoalFound
        #print "Self: {}".format(self.xy)
        #print "Current Goal: {}".format(currentGoalXY)
        if tuple(self.xy) == currentGoalXY:
            global goalNode
            goalNode = self
            currentGoalFound = True
            return True
        else:
            currentGoalFound = False
            return False

    def rebuildCost(self):
        self.costFromStart = 0
        p = self.parent
        while p:
            self.costFromStart += 1
            p = p.parent

def printProblem(path):
    for node in path:
        THE_PROBLEM[node[0],node[1]] = bcolors.FAIL + TRAVERSED_CELL + bcolors.ENDC
    #os.system('clear')
    THE_PROBLEM[currentStartingNodeXY[0],currentStartingNodeXY[1]] = bcolors.OKBLUE + GOAL_CELL + bcolors.ENDC
    THE_PROBLEM[currentGoalXY[0],currentGoalXY[1]] = bcolors.OKGREEN + GOAL_CELL + bcolors.ENDC
    print '\n'
    print '\n'.join(''.join(str(cell) for cell in x) for x in THE_PROBLEM)

def printPath(node):
    forwardPath = []
    p = node.parent
    while p:
        forwardPath.append(p)
        p = p.parent

    cell = forwardPath.pop()
    while forwardPath:
        if THE_PROBLEM[cell.xy[0],cell.xy[1]] == START_CELL: 
            cell = forwardPath.pop()
            continue
        THE_PROBLEM[cell.xy[0],cell.xy[1]] = bcolors.OKGREEN + TRAVERSED_CELL + bcolors.ENDC
        cell = forwardPath.pop()
        print '\n'
        print '\n'.join(''.join(str(cell) for cell in x) for x in THE_PROBLEM)
        time.sleep(.07)

def resetProblem():
    for line in THE_PROBLEM:
        for cell in line:
            idx = numpy.where(THE_PROBLEM==cell)
            if "*" in cell: THE_PROBLEM[idx] = SPACE_CELL

    for item in goalNodesXY:
        THE_PROBLEM[item[0],item[1]] = GOAL_CELL

    THE_PROBLEM[currentStartingNodeXY[0],currentStartingNodeXY[1]] = bcolors.OKBLUE + GOAL_CELL + bcolors.ENDC

def isInFrontier(node):
    for f in theFrontier:
        if node.xy == f[1].xy:
            return True
    return False
# ---------------------  END DECLARATIONS & DEFINITIONS  ------------------- #
# -------------------------------------------------------------------------- #

startTime = time.time()

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
            if ch == 'P':
                startingNodeXY = (y,x)
                print "Start: {}".format(startingNodeXY)
            elif ch == '+':
                goalNodesXY.append((y,x))
                print "Goal Added: {}".format((x,y))
            x += 1
        x = 0
        y += 1

    #starting state
    print '\n'.join(''.join(str(cell) for cell in x) for x in THE_PROBLEM)

# ----------------------------------------- #
# --------- START PRIMARY LOGIC ----------- #
# ----------------------------------------- #

# The final state holder node
GoldenGoalNode = None

currentStartingNodeXY = startingNodeXY
currentGoalNodesXY = copy.deepcopy(goalNodesXY)
Broke = False

# -------------------------------------------------------------- #
# The general idea behind this is the Nearest Neighbor Algorithm
# Though I'd come up with the algorithm before realizing it was
# already a thing, I feel like I should add the reference anyway:
# -- http://en.wikipedia.org/wiki/Nearest_neighbour_algorithm
# -------------------------------------------------------------- #

# -------- Primary Loop -------- #
# For every goal in the problem
for g in goalNodesXY:
    print "Current Global Goal Node XY: {}".format(g)
    currentBestGoalCost = 999999
    # Find shortest path to each goal (g)
    for goalXY in currentGoalNodesXY[:]:
        print '*' * 100
        currentGoalXY = goalXY
        print "Current Goal XY: {}".format(goalXY)

        currentGoalFound = False
        del CHECKED_NODES[:]

        startNode = Node()
        startNode.setLocation(currentStartingNodeXY)
        print "Starting Point: {}".format(currentStartingNodeXY)

        goalNode = Node()
        goalNode.setLocation(currentGoalXY)

        stateNode = startNode
        stateNode.populateMoves()
        stateNode.checkGoal()

        theFrontier = []
        # Populate frontier with 'start copy' as only available Node
        heapq.heappush(theFrontier, (stateNode.heuristic, stateNode)) 

        while not currentGoalFound and theFrontier:
            # heappop returns tuple of (weighted-idx, data)
            stateNode = heapq.heappop(theFrontier)[1]
            CHECKED_NODES.append(stateNode.xy)

            # If the cost is higher than one we've found, break and continue to next
            if stateNode.heuristic > currentBestGoalCost: 
                Broke = True
                break

            while stateNode.moves and not currentGoalFound:
                EXPANDED_NODES += 1
                moveDirection = heapq.heappop(stateNode.moves)[1]
                nextNode = Node()
                nextNode.setParent(stateNode)
                nextNode.setLocation((stateNode.xy[0] + moveDirection[0], stateNode.xy[1] + moveDirection[1]))
                if nextNode.xy not in CHECKED_NODES and not isInFrontier(nextNode):
                    if nextNode.checkGoal(): break
                    nextNode.populateMoves()
                    heapq.heappush(theFrontier, (nextNode.heuristic,nextNode))
                    CHECKED_NODES.append(nextNode.xy)
        
            #pretty print
            #printProblem(CHECKED_NODES)
            #time.sleep(SLEEPER)

        # Hacky logic to skip the below bits
        if Broke:
            Broke = False
            continue

        # Push the current goal node onto the heap
        heapq.heappush(weightedGoalNodes, (goalNode.costFromStart, goalNode))
        
        # If we've made it this far, update our checker
        currentBestGoalCost = goalNode.heuristic
        resetProblem()

    # Current goal (g)'s next hop:
    nextHop = heapq.heappop(weightedGoalNodes)
    if not GoldenGoalNode: 
        GoldenGoalNode = nextHop[1]
    else:
        tmp = GoldenGoalNode
        GoldenGoalNode = nextHop[1]
        p = GoldenGoalNode.parent
        while p.parent:
            p = p.parent
        p.parent = tmp

    # We have a path for this one, remove it from the list
    currentGoalNodesXY.remove(tuple(nextHop[1].xy))

    # Update the location from where we'll start our next A* search
    global currentStartingNodeXY
    currentStartingNodeXY = nextHop[1].xy
    weightedGoalNodes = []

# Print Final Results
totalTime = time.time() - startTime
par = GoldenGoalNode.parent
while par:
    print par.xy
    par = par.parent

printProblem(CHECKED_NODES)
printPath(GoldenGoalNode)
print "Nodes Expanded:  {}".format(EXPANDED_NODES)
GoldenGoalNode.rebuildCost()
print "Path Cost: {}".format(GoldenGoalNode.costFromStart)
print "Total Calculation Time: {} seconds".format(totalTime)