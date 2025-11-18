import sys
import math


# Robot Class
class Robot:
    def __init__(self, rid, x, y, item):
        self.rid = rid
        self.x = x
        self.y = y
        self.item = item
        self.command = "WAIT"
        self.role = None

    def update(self, x, y, item):
        self.x = x
        self.y = y
        self.item = item

    def is_in_hq(self):
        return self.x == 0
    
    def has_item(self):
        return self.item

    def set_command(self, cmd):
        self.command = cmd

    def is_alive(self):
        return self.x != -1 and self.y != -1

    def __str__(self):
        return self.command


# Assign roles to robots
def assign_roles(robots, radar: bool, trap: bool):
    alive = sorted([r for r in robots.values() if r.is_alive()], key=lambda r: r.rid)

    for r in alive:
        r.role = "mine"

    if radar and len(alive) > 1:
        alive[0].role = "radar"

    if trap and len(alive) > 1:
        alive[1 if radar else 0].role = "trap"


# Radar placments
def radar_placment(my_radars):
    radar_placments = [(5, 7), (13, 7), (21, 7)]

    for pos in radar_placments:
        if pos not in my_radars:
            return pos  
    return None


# Get closest ore positions
def get_closest_ore_positions(ore_map, robot_x, robot_y):
    ore_positions = []

    height = len(ore_map)
    width = len(ore_map[0])

    for y in range(height):
        for x in range(width):
            cell = ore_map[y][x]
            if cell.isdigit() and int(cell):
                dist = abs(robot_x - x) + abs(robot_y - y)
                ore_positions.append(((x, y), dist))

    ore_positions.sort(key=lambda p: p[1])

    return [pos for pos, _ in ore_positions]


width, height = [int(i) for i in input().split()]

ore_map = [["?" for _ in range(width)] for _ in range(height)]

robots = {}

# game loop
while True:

    my_radars = []
    shared_targets = []

    # Update score
    my_score, opponent_score = [int(i) for i in input().split()]

    # Update map
    for i in range(height):
        inputs = input().split()

        for j in range(width):
            ore = inputs[2*j]
            hole = int(inputs[2*j+1])

            if ore != "?":
                ore_map[i][j] = ore
    
    # Update entities
    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    for i in range(entity_count):
        entity_id, entity_type, x, y, item = [int(j) for j in input().split()]

        if entity_type == 0:
            if entity_id not in robots:
                robots[entity_id] = Robot(entity_id, x, y, item)

            else:
                robots[entity_id].update(x, y, item)
        
        if entity_type == 2:
            my_radars.append((x, y))

    # Assign roles
    assign_roles(robots, radar_placment(my_radars) is not None, False)

    # Control robots
    for r in robots.values():
        # Dead robots
        if not r.is_alive():
            r.set_command("WAIT")

        # Radar robot
        if r.role == 'radar':
            target = radar_placment(my_radars)
            target_x, target_y = target if target else [0, 0]

            if r.is_in_hq() and r.has_item() != 2 and radar_cooldown == 0:
                r.set_command("REQUEST RADAR")

            elif r.is_in_hq() and r.has_item() == 2:
                r.set_command(f"MOVE {target_x} {target_y}")

            elif not r.is_in_hq() and r.has_item() ==2:
                r.set_command(f"DIG {target_x} {target_y}")

            elif not r.is_in_hq() and r.has_item() != 2:
                r.set_command(f"MOVE 0 7")

        # Trap robot

        # Miner robots
        if r.role == 'mine':
            closest_ores = get_closest_ore_positions(ore_map, r.x, r.y)

            target_x, target_y = (5, r.y)
            
            if closest_ores:
                closest_ores = [pos for pos in closest_ores if pos not in shared_targets]
                target = closest_ores[0] if closest_ores else (5, r.y)
                target_x, target_y = target if target else (5, r.y)
                shared_targets.append(target)

            if r.is_in_hq():
                r.set_command(f"MOVE {target_x} {target_y}")

            if not r.is_in_hq() and r.has_item() != 4 and len(shared_targets) > 0:
                r.set_command(f"DIG {target_x} {target_y}")
                
            if not r.is_in_hq() and r.has_item() == 4:
                r.set_command(f"MOVE {0} {r.y}")
 
        print(r)
