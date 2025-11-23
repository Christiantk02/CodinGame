import sys
import math
import numpy as np
from collections import deque

class GameState:
    def __init__(self, width, height, grid):
        self.width = width
        self.height = height

        self.grid = grid
        self.pellet_grid = [[0 for _ in range(width)] for _ in range(height)]

        self.visible_pac_count = 0
        
        self.my_score = 0
        self.opponent_score = 0

        self.my_pacs = {}
        self.opponent_pacs = {}

        self.shared_targets = {}

class Pac:
    def __init__(self, p_id, x, y):
        self.p_id = p_id
        self.x = x
        self.y = y

    def update(self, x, y):
        self.x = x
        self.y = y


def update_game(state: GameState):
    state.my_score, state.opponent_score = [int(i) for i in input().split()]
    state.visible_pac_count = int(input())

    for i in range(state.visible_pac_count):
        inputs = input().split()
        pac_id = int(inputs[0])
        mine = inputs[1] != "0"

        x = int(inputs[2])
        y = int(inputs[3])

        if mine:
            if pac_id not in state.my_pacs:
                state.my_pacs[pac_id] = Pac(pac_id, x, y)
            else:
                state.my_pacs[pac_id].update(x, y)
        else:
            if pac_id not in state.opponent_pacs:
                state.opponent_pacs[pac_id] = Pac(pac_id, x, y)
            else:
                state.opponent_pacs[pac_id].update(x, y)

        type_id = inputs[4]
        speed_turns_left = int(inputs[5])
        ability_cooldown = int(inputs[6])

    visible_pellet_count = int(input())

    state.pellet_grid = [[0 for _ in range(width)] for _ in range(height)]

    for i in range(visible_pellet_count):
        x, y, value = [int(j) for j in input().split()]
        state.pellet_grid[y][x] = value

def bfs(state: GameState, goal, start):
    visited = []
    queue = deque()
    visited.append(start)
    queue.append(start)

    while queue:
        (x, y) = queue.popleft()

        if int(state.pellet_grid[y][x]) == goal:
            return (x, y)
        else:
            for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                if (0 <= nx < state.width and 0 <= ny < state.height) and state.grid[ny][nx] != "#" and (nx, ny) not in visited :
                    visited.append((nx, ny))
                    queue.append((nx, ny))
    return None


width, height = [int(i) for i in input().split()]

grid = []
for i in range(height):
    row = input() 
    grid.append(list(row))

game = GameState(width, height, grid)

# game loop
while True:
    update_game(game)

    x = 10
    y = 10

    command = []
    for pac in game.my_pacs.values():
        target = bfs(game, 10, (pac.x, pac.y)) 
        
        if not target:
            target = bfs(game, 1, (pac.x, pac.y)) 

        x, y = target if target else (0, 0)

        command.append(f"MOVE {pac.p_id} {x} {y}")

    print(" | ".join(command))
    