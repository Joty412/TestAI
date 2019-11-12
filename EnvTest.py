import numpy as np
from PIL import Image
import cv2

LENGTH = 4

ROAD_N = 1  # player key in dict
CAR_N = 2  # food key in dict
ENEMY_N = 3  # enemy key in dict

# the dict! Using just for colors
d = {1: (255, 255, 255),  # blueish color
     2: (0, 255, 0),  # green
     3: (0, 0, 255)}  # red


env = np.zeros((LENGTH*2 + 1, LENGTH*2 + 1, 3), dtype=np.uint8)
for i in range(LENGTH*2):
    env[LENGTH][i] = d[ROAD_N]
    env[LENGTH][(2*LENGTH - i)] = d[ROAD_N]
    env[i][LENGTH] = d[ROAD_N]
    env[2*LENGTH - i][LENGTH] = d[ROAD_N]
    img = Image.fromarray(env, 'RGB')
    img = img.resize((300, 300))
    cv2.imshow("image", np.array(img))
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break
