import sys
import numpy as np
import math


# To debug: print("Debug messages...", file=sys.stderr, flush=True)

# You have to output the target position
# followed by the power (0 <= thrust <= 100)
# i.e.: "x y thrust"

class PID:
    def __init__(self, kp: float, ki: float, kd: float, ts: float):
        self.kp = kp 
        self.ki = ki
        self.kd = kd
        self.ts = ts
        self.prev_error = 0
        self.integral = 0

    def compute(self, sp, pv):
        error = sp - pv
        self.integral += error * self.ts
        P = self.kp * error
        I = self.ki * self.integral
        D = self.kd * ((error - self.prev_error) / self.ts)

        return P + I + D

pid_speed = PID(kp=0.03, ki=0.0003, kd=0.01 * 0.03, ts=1)

thrust = 0
boost_used = False

# Game Loop
while True:
    # Get Game Data
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    if abs(next_checkpoint_angle) > 90:
        thrust = 1
    else:
        speed = pid_speed.compute(next_checkpoint_dist, 0)
        thrust= int(max(0, min(100, speed)))

    if not(boost_used) and abs(next_checkpoint_angle) < 2 and next_checkpoint_dist > 5000:
        thrust = "BOOST"
        print("BOOST USED", file=sys.stderr, flush=True)
        boost_used = True

    print(next_checkpoint_x, next_checkpoint_y, thrust)
