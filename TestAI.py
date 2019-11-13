import numpy as np
from PIL import Image
import cv2

LENGTH = 4

HM_EPISODES = 1
STEPS = 400
MOVE_PENALTY = 1  # feel free to tinker with these!
ENEMY_PENALTY = 300  # feel free to tinker with these!
CAR_REWARD = 1  # feel free to tinker with these!
epsilon = 0.5  # randomness
EPS_DECAY = 0.9999  # Every episode will be epsilon*EPS_DECAY
SHOW_EVERY = 1  # how often to play through env visually.

start_q_table = None  # if we have a pickled Q table, we'll put the filename of it here.

LEARNING_RATE = 0.1
DISCOUNT = 0.95

ROAD_N = 1  # player key in dict
CAR_N = 2  # food key in dict
ENEMY_N = 3  # enemy key in dict

# the dict! Using just for colors
d = {1: (255, 255, 255),  # blueish color
     2: (0, 255, 0),  # green
     3: (0, 0, 255)}  # red


class Car:
    def __init__(self, start):
        self.position = 0
        self.start = start

    def move(self):
        if self.position <= LENGTH:
            if self.position == LENGTH - 1:
                if traffic_light == self.start:
                    self.position += 1
                    grid[self.start][self.position - 1] = False
            elif self.position == 0:
                self.position += 1
                grid[self.start][self.position] = True
            elif not grid[self.start][self.position + 1]:
                self.position += 1
                grid[self.start][self.position - 1] = False
                grid[self.start][self.position] = True
        if self.position == LENGTH + 1:
            self.position += 1
            return True
        else:
            return False


if start_q_table is None:
    q_table = [[[[None]*LENGTH]*LENGTH]*LENGTH]*LENGTH
    for lane1 in range(LENGTH):
        for lane2 in range(LENGTH):
            for lane3 in range(LENGTH):
                for lane4 in range(LENGTH):
                    q_table[lane1][lane2][lane3][lane4] = [np.random.uniform(-5, 0) for i in range(4)]

print(q_table)

episode_rewards = []

for episode in range(HM_EPISODES):
    if episode % SHOW_EVERY == 0:
        show = True
    else:
        show = False

    grid = [[False]*LENGTH, [False]*LENGTH, [False]*LENGTH, [False]*LENGTH]
    cars = [[], [], [], [], []]
    number_of_cars = 0

    for step in range(STEPS):
        if 0 == np.random.randint(0, 2):
            lane = np.random.randint(0, 4)
            cars[lane].append(Car(lane))
        for lane in cars:
            car_to_remove = None
            for car in lane:
                if car.move():
                    number_of_cars += 1
#           lane.remove(car_to_remove)
        obs = q_table[len(cars[0])][len(cars[1])][len(cars[2])][len(cars[3])]
        if np.random.random() > epsilon:
            action = np.argmax(obs)
        else:
            action = np.random.randint(0, 4)

        traffic_light = 5

        if show:
            env = np.zeros((LENGTH*2 + 1, LENGTH*2 + 1, 3), dtype=np.uint8)
            for i in range(LENGTH):
                env[LENGTH][i] = d[ROAD_N]
                env[LENGTH][(2*LENGTH - i)] = d[ROAD_N]
                env[i][LENGTH] = d[ROAD_N]
                env[2*LENGTH - i][LENGTH] = d[ROAD_N]
            for lane in range(len(grid)):
                for i in range(len(grid[lane])):
                    if grid[lane][i]:
                        if lane == 0:
                            env[LENGTH][i] = d[CAR_N]
                        elif lane == 1:
                            env[2*LENGTH - i][LENGTH] = d[CAR_N]
                        elif lane == 3:
                            env[LENGTH][2*LENGTH - i] = d[CAR_N]
                        else:
                            env[i][LENGTH] = d[CAR_N]
            img = Image.fromarray(env, 'RGB')
            img = img.resize((300, 300))
            cv2.imshow("image", np.array(img))
            if cv2.waitKey(1000) & 0xFF == ord('q'):
                break
        print(step)
