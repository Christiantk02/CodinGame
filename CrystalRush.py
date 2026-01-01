import sys
import math


# Robot Class
class Robot:
    def __init__(self, rid, x, y, item):
        self.rid = rid

        self.x = x
        self.y = y

        self.last_x = self.x 
        self.last_y = self.y

        self.item = item

        self.command = "WAIT"

        self.role = None

    def update(self, x, y, item):
        self.last_x = self.x 
        self.last_y = self.y

        self.x = x
        self.y = y

        self.item = item

    def is_in_hq(self):
        return self.x == 0

    def has_item(self):
        return self.item == 1
    
    def has_radar(self):
        return self.item == 2

    def has_trap(self):
        return self.item == 3

    def has_ore(self):
        return self.item == 4

    def set_command(self, cmd):
        self.command = cmd

    def is_alive(self):
        return self.x != -1

    def __str__(self):
        return self.command

    def debug(self):
        print(f"[Robot {self.rid}] " f"pos=({self.x},{self.y}) " f"last pos=({self.last_x},{self.last_y})" f"item={self.item}" f"role={self.role}" f"alive={self.is_alive()} ", file=sys.stderr)


# Game Class
class GameState:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.my_score = 0
        self.opponent_score = 0

        self.discovered_tiles = 0

        self.reserved_ores = {}

        self.ore_map = [["?" for _ in range(width)] for _ in range(height)]

        self.hole_map = [[0 for _ in range(width)] for _ in range(height)]
        self.old_hole_map = self.hole_map

        self.radar_heuristics = [[0.0 for _ in range(width)] for _ in range(height)]
        self.trap_heuristics = [[0.0 for _ in range(width)] for _ in range(height)]

        self.robots = {}
        self.opponent_robots = {}

        self.my_radars = []
        self.my_traps = []
  
        self.potential_traps = []

        self.radar_cooldown = 0
        self.trap_cooldown = 0


# Update game
def update(state: GameState):
    state.my_score, state.opponent_score = map(int, input().split())

    state.old_hole_map = [row.copy() for row in state.hole_map]

    for i in range(state.height):
        row = input().split()
        for j in range(state.width):
            ore = row[2*j]
            hole = int(row[2*j + 1])

            state.ore_map[i][j] = ore

            state.hole_map[i][j] = hole

    entity_count, state.radar_cooldown, state.trap_cooldown = map(int, input().split())

    state.discovered_tiles = sum(1 for row in state.ore_map for cell in row if cell.isdigit())

    state.my_radars = []
    state.my_traps = []

    for _ in range(entity_count):
        entity_id, entity_type, x, y, item = map(int, input().split())

        if entity_type == 0:
            if entity_id not in state.robots:
                state.robots[entity_id] = Robot(entity_id, x, y, item)
            else:
                state.robots[entity_id].update(x, y, item)
        
        elif entity_type == 1:
            if entity_id not in state.opponent_robots:
                state.opponent_robots[entity_id] = Robot(entity_id, x, y, item)
            else:
                state.opponent_robots[entity_id].update(x, y, item)

        elif entity_type == 2:
            state.my_radars.append((x, y))

        elif entity_type == 3:
            state.my_traps.append((x, y))


# Assign roles for robots
def assign_roles(state: GameState):
    robots = sorted(state.robots.values(), key=lambda r: r.rid)

    robots[0].role = "RADAR"
    robots[1].role = "TRAP"
    robots[2].role = "MINER"
    robots[3].role = "MINER"
    robots[4].role = "MINER"


# Update potential traps
def update_potential_traps(state: GameState):

    if len(state.potential_traps) > 50:
        state.potential_traps.pop(0)

    for robot in state.opponent_robots.values():
        if not robot.is_alive():
            continue

        if robot.x == robot.last_x and robot.y == robot.last_y:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    
                    x = robot.x + dx
                    y = robot.y + dy

                    if not (0 <= x < state.width and 0 <= y < state.height):
                        continue

                    if state.hole_map[y][x] != state.old_hole_map[y][x] and (x, y) not in state.potential_traps:
                        state.potential_traps.append((x, y))


# Get neighbouring cells
def radar_cells(x, y, state: GameState):
    cells = []

    for dx in range(-4, 5, 1):
        for dy in range(-4, 5, 1):
            nx = x + dx
            ny = y + dy

            if 0 <= nx < state.width and 0 <= ny < state.height:
                cells.append((nx, ny))

    return cells


# Update radar and trap heuristics
def update_huristic(state: GameState):

    # Radar weights
    radar_frontier_penalty = 3
    radar_trap_risk_penalty = 3
    radar_occupied_cell_penalty = 10
    radar_radar_dist_penalty = 2
    radar_unknown_cells_reward = 2
    radar_holes_penalty = 0.05

    # Trap weights
    trap_frontier_penalty = 3
    trap_risk_penalty = 3
    trap_occupied_cell_penalty = 10
    trap_ore_reward = 5
    trap_potential_traps = 5

    for y in range(state.height):
        for x in range(state.width):
            radar_score = 0
            trap_score = 0

            # Dist from HQ
            radar_score -= (x / state.width) * radar_frontier_penalty
            trap_score -= (x / state.width) * trap_frontier_penalty

            # Potential trap or occupied
            if (x, y) in state.potential_traps:
                radar_score -= 1 * radar_trap_risk_penalty
                trap_score -= 1 * trap_risk_penalty

            if (x, y) in state.my_radars or (x, y) in state.my_traps:
                radar_score -= 1 * radar_occupied_cell_penalty
                trap_score -= 1 * trap_occupied_cell_penalty

            # Dist from last radar
            if state.my_radars:
                last_radar = state.my_radars[-1]
                dist = abs(x - last_radar[0]) + abs(y - last_radar[1])
                radar_score -= (dist / (state.width + state.height)) * radar_radar_dist_penalty

            # Reward if cell is ore
            if state.ore_map[y][x].isdigit():
                trap_score += int(state.ore_map[y][x]) * trap_ore_reward

            # Loop for neighbours
            cells = radar_cells(x, y, state)
            unknowns = 0
            holes = 0
            potential_traps = 0

            for cx, cy in cells:
                ore = state.ore_map[cy][cx]
                hole = state.hole_map[cy][cx]

                if ore == "?":
                    unknowns += 1

                if hole == 1:
                    holes += 1

                if (cx, cy) in state.potential_traps:
                    potential_traps += 1

            radar_score += (unknowns / 9) * radar_unknown_cells_reward
            radar_score -= (holes / 9) * radar_holes_penalty

            trap_score += (potential_traps / 9) * trap_potential_traps

            # If cell in hq
            if x == 0:
                radar_score = -1000
                trap_score = -1000

            state.radar_heuristics[y][x] = radar_score
            state.trap_heuristics[y][x] = trap_score


# Control radar robot
def control_radar(state: GameState, robot: Robot):
    placements = []

    if not robot.is_alive():
        robot.set_command("WAIT")
        return

    if state.discovered_tiles >= 0.75 * (29 * 14):
        control_miner(state, robot)
        return

    for y in range(state.height):
        for x in range(state.width):
            placements.append((x, y, state.radar_heuristics[y][x]))
    
    placements.sort(key=lambda c: c[2], reverse=True)

    if not robot.has_radar():
        robot.set_command("REQUEST RADAR")
    else:
        x, y, _= placements[0]
        robot.set_command(f"DIG {x} {y}")


# Control trap robot
def control_trap(state: GameState, robot: Robot):
    placements = []

    if not robot.is_alive():
        robot.set_command("WAIT")
        return

    for y in range(state.height):
        for x in range(state.width):
            placements.append((x, y, state.trap_heuristics[y][x]))
    
    placements.sort(key=lambda c: c[2], reverse=True)

    if not robot.has_trap():
        robot.set_command("REQUEST TRAP")
    else:
        x, y, _= placements[0]
        robot.set_command(f"DIG {x} {y}")


# Get closest ore for miners
def get_mining_target(state: GameState, robot: Robot):

    if robot.rid in state.reserved_ores:
        x, y = state.reserved_ores[robot.rid]
        ore = state.ore_map[y][x]

        if ore.isdigit() and int(ore) > 0 and (x, y) not in state.potential_traps and (x, y) not in state.my_traps:
            return (x, y)
        else:
            del state.reserved_ores[robot.rid]
    
    best_dist = 100
    best = None

    for x in range(state.width):
        for y in range(state.height):

            ore = state.ore_map[y][x]
            if not ore.isdigit() or int(ore) <= 0:
                continue

            if (x, y) in state.potential_traps:
                continue

            if (x, y) in state.reserved_ores.values():
                continue

            if (x, y) in state.my_traps:
                continue

            dist = abs(robot.x - x) + abs(robot.y - y) + 1.5 * x

            if dist < best_dist:
                best_dist = dist
                best = (x, y)

    return best


# Control miners
def control_miner(state: GameState, robot: Robot):

    if not robot.is_alive():
            robot.set_command("WAIT")
            return
    
    if robot.has_ore():
        robot.set_command(f"MOVE {0} {robot.y}")

        if robot.rid in state.reserved_ores:
            del state.reserved_ores[robot.rid]

    else:
        target = get_mining_target(state, robot)

        if target:
            x, y = target
            state.reserved_ores[robot.rid] = (x, y)
            robot.set_command(f"DIG {x} {y}")
        else:
            robot.set_command(f"MOVE {5} {robot.y}")


# Variables
width, height = [int(i) for i in input().split()]

game = GameState(width, height)


# game loop
while True:

    # Updating functions
    update(game)
    assign_roles(game)
    update_potential_traps(game)
    update_huristic(game)
    

    # Control for loop
    for robot in game.robots.values():

        if robot.role == "RADAR":
            control_radar(game, robot)

        if robot.role == "MINER":
            control_miner(game, robot)

        if robot.role == "TRAP":
            control_trap(game, robot)

        print(robot)