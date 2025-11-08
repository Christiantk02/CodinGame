import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# w: width of the building.
# h: height of the building.
w, h = [int(i) for i in input().split()]
n = int(input())  # maximum number of turns before game over.
x0, y0 = [int(i) for i in input().split()]

Min_x, Max_x = 0, w
Min_y, Max_y = 0, h

Move_x, Move_y = 0,0

# game loop
while True:
    bomb_dir = input()  # the direction of the bombs from batman's current location (U, UR, R, DR, D, DL, L or UL)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    if "D" in bomb_dir:
        Min_y = y0
    if "U" in bomb_dir:
        Max_y = y0
    if "R" in bomb_dir:
        Min_x = x0
    if "L" in bomb_dir:
        Max_x = x0

    x0 = (Max_x + Min_x) // 2
    y0 = (Max_y + Min_y) // 2

    # the location of the next window Batman should jump to.
    print(x0 ,y0)
