import sys
import math
from collections import deque

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# r: number of rows.
# c: number of columns.
# a: number of rounds between the time the alarm countdown is activated and the time the alarm goes off.
r, c, a = [int(i) for i in input().split()]

maze = [["?" for _ in range(c)] for _ in range(r)]
controllRoomPos = None

goHome = False
goal = "?"

class Node:
  def __init__(self, r, c, parent=None):
    self.r = r
    self.c = c
    self.parent = parent

def BFS(root, goal):

    queue = deque()
    visited = set()

    queue.append(root)
    visited.add((root.r, root.c))

   

    while queue:
        currentNode = queue.popleft()

        if maze[currentNode.r][currentNode.c] == goal:

            path = []
            m = currentNode
            
            while m != root:
                path.append(m)
                m = m.parent
            
            path.reverse()
            return path

    
        for dirR, dirC in [(-1,0),(1,0),(0,-1),(0,1)]:
            neighbour = Node(currentNode.r+dirR , currentNode.c + dirC, currentNode)
            if 0 <= neighbour.r < r and 0 <= neighbour.c < c and maze[neighbour.r][neighbour.c] != "#" and (neighbour.r, neighbour.c) not in visited:
                if goal != "?" and maze[neighbour.r][neighbour.c] == "?": 
                    continue
                visited.add((neighbour.r, neighbour.c))
                queue.append(neighbour)     
    return []

# game loop
while True:
    # kr: row where Rick is located.
    # kc: column where Rick is located.
    kr, kc = [int(i) for i in input().split()]

    if (kr, kc) == controllRoomPos:
        goHome = True
        goal = "T"

    for i in range(r):
        row = input()  # C of the characters in '#.TC?' (i.e. one line of the ASCII maze).
        maze[i] = list(row)
  
        if "C" in row and not(goHome):
            controllRoomPos = (i, row.index("C"))
            path = len(BFS(Node(*controllRoomPos),"T"))
            if path != 0 and path-a <= 0:
                goal = "C"
        
    move = BFS(Node(kr,kc),goal)

    if move[0].r < kr:
        print("UP")
    elif move[0].r > kr:
        print("DOWN")
    elif move[0].c < kc:
        print("LEFT")
    elif move[0].c > kc:
        print("RIGHT")

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # Rick's next move (UP DOWN LEFT or RIGHT).
    print("\n".join("".join(line) for line in maze), file=sys.stderr, flush=True)