from VissimController import VissimController
import numpy as np


DIRECTIONS = 4
EXITS = 3
MAXIMUM_INPUT_FLOW = 2000


class Environment:
    def __init__(self):
        self.vissim = VissimController()

    def reset(self):
        # Set the vehicle flow and routing decision values
        for direction in range(DIRECTIONS):
            self.vissim.set_vehicle_input(np.random.randint(0, MAXIMUM_INPUT_FLOW), direction + 1)
            for exit_direction in range(EXITS):
                self.vissim.set_vehicle_direction(np.random.rand(), direction + 1, exit_direction + 1)

        # Start simulation
        self.vissim.initiate_simulation()

        # Set all lights to red
        for light in range(1, DIRECTIONS * EXITS + 1):
            self.vissim.set_signal_state(light, 'RED')

        # Change to random first state
        self.current_phase = np.random.randint(0, 13)
        self.vissim.change_signal_state(13, self.current_phase)

        # AI properties
        self.episode_step = 0
        return np.array(self.vissim.get_current_vehicle_state())

    def step(self, action):
        self.episode_step += 1
        if not action:
            self.vissim.run_step()
            new_observation = np.array(self.vissim.get_current_vehicle_state())
        else:
            self.vissim.change_signal_state(self.current_phase, action, self)
            self.current_phase = action
            self.vissim.run_step()
            new_observation = np.array(self.vissim.get_current_vehicle_state())

        if self.episode_step == 600:
            reward = self.vissim.get_reward()
            done = True
        else:
            reward = 0
            done = False

        return new_observation, reward, done


