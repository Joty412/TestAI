from tensorflow import keras
from collections import deque
from ModifiedTensorBoard import ModifiedTensorBoard
from tensorflow.keras.callbacks import TensorBoard
from PIL import Image
from tqdm import tqdm
import numpy as np
import time
import random
import cv2
import os


# Inputs
REPLAY_MEMORY_SIZE = 50000
AGGREGATE_STATS_EVERY = 50  # episodes
SHOW_PREVIEW = False

ACTION_SPACE_SIZE = 13
MODEL_NAME = "Test"
MAX_VALUE = 255
MIN_REPLAY_MEMORY_SIZE = 1000
MINIBATCH_SIZE = 64
DISCOUNT = 0.99
UPDATE_TARGET_EVERY = 5
EPISODES = 20
MIN_REWARD = -200

epsilon = 1  # not a constant, going to be decayed
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.001

random.seed(1)
np.random.seed(1)


class Agent:
    @staticmethod
    def create_model():
        model = keras.Sequential()

        model.add(keras.layers.Conv2D(256, (3, 3), input_shape=(10, 10, 3)))
        model.add(keras.layers.Activation('relu'))
        model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
        model.add(keras.layers.Dropout(0.2))

        model.add(keras.layers.Conv2D(256, (3, 3)))
        model.add(keras.layers.Activation('relu'))
        model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
        model.add(keras.layers.Dropout(0.2))

        model.add(keras.layers.Flatten())
        model.add(keras.layers.Dense(64))

        model.add(keras.layers.Dense(ACTION_SPACE_SIZE))
        model.compile(loss='mse', optimizer=keras.optimizers.Adam(lr=0.001), metrics=['accuracy'])

        return model

    def __init__(self):
        self.model = self.create_model()
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())
        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        self.tensorboard = TensorBoard(log_dir="logs/{}-{}".format(MODEL_NAME, int(time.time())))
        self.target_update_counter = 0

    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def get_qs(self, state):
        return self.model.predict(np.array(state).reshape(-1, *state.shape)/MAX_VALUE)[0]

    def train(self, terminal_state, step):
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)
        current_states = np.array([transition[0] for transition in minibatch])/MAX_VALUE
        current_qs_list = self.model.predict(current_states)

        new_current_states = np.array([transition[3] for transition in minibatch])/MAX_VALUE
        future_qs_list = self.target_model.predict(new_current_states)

        x = []
        y = []

        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            x.append(current_state)
            y.append(current_qs)

        self.model.fit(np.array(x)/MAX_VALUE, np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False)

        if terminal_state:
            self.target_update_counter += 1

        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0



env =

ep_rewards = [-200]

if not os.path.isdir('models'):
    os.makedirs('models')

agent = Agent()

for episode in tqdm(range(1, EPISODES + 1), ascii=True, unit='episodes'):
    agent.tensorboard.step = episode
    episode_reward = 0
    step = 1
    current_state = env.reset()
    done = False
    while not done:
        if np.random.random() > epsilon:
            action = np.argmax(agent.get_qs(current_state))
        else:
            action = np.random.randint(0, env.ACTION_SPACE_SIZE)

        new_state, reward, done = env.step(action)
        episode_reward += reward

        if SHOW_PREVIEW and not episode % AGGREGATE_STATS_EVERY:
            env.render()

        agent.update_replay_memory((current_state, action, reward, new_state, done))
        agent.train(done, step)
        current_state = new_state
        step += 1

        if not episode % AGGREGATE_STATS_EVERY or episode == 1:
            average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:]) / len(ep_rewards[-AGGREGATE_STATS_EVERY:])
            min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
            max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])
            #agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward,
            #                               epsilon=epsilon)

            # Save model, but only when min reward is greater or equal a set value
            #if average_reward >= MIN_REWARD:
            #    agent.model.save(
            #       f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

        # Decay epsilon
        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON, epsilon)
