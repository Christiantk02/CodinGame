import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

lowest = 10000
n = int(input())  # the number of temperatures to analyse

if n == 0:
    lowest = 0

for i in input().split():
    # t: a temperature expressed as an integer ranging from -273 to 5526
    t = int(i)
    if abs(t) < abs(lowest):
        lowest = t

    if lowest == t*-1:
        lowest = abs(t)
  

# Write an answer using print
# To debug: print("Debug messages...", file=sys.stderr, flush=True)

print(lowest)
