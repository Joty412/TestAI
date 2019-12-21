import os
import win32com.client as com
import time

# Inputs
NETWORK_FILE_NAME = 'Junction.inpx'
LAYOUT_FILE_NAME = 'Junction.layx'
LANE_LENGTH = 200
DISCRETE_LENGTH = 5
SIGNAL_CONTROL_NUMBER = 1
NUMBER_OF_LANES = 12
DIRECTIONS = 4
AMBER_TIME = 2
REDAMBER_TIME = 1
INTERPHASE_TIME = 2
MIN_GREEN_TIME = 5

# Calculated Inputs
DISCRETE_AMOUNT = int(LANE_LENGTH/DISCRETE_LENGTH)

# Phases    123456789ABC
phases = [0b001100001100,
          0b100001100001,
          0b000011000011,
          0b011000011000,
          0b000000001111,
          0b000001111000,
          0b001111000000,
          0b111000000001,
          0b000001001011,
          0b001001011000,
          0b001011000001,
          0b011000001001,
          0b001001001001,
          0b000000000000]

# Directions
North = 2
East = 3
South = 4
West = 1

Left = 3
Right = 1
Straight = 2


class VissimController:
    def __init__(self):
        # Register vissim COM
        self.vissim = com.gencache.EnsureDispatch("vissim.vissim")
        
        # Load vissim network and layout
        current_directory = os.getcwd()
        file_name = os.path.join(current_directory, NETWORK_FILE_NAME)
        self.vissim.LoadNet(file_name, False)
        file_name = os.path.join(current_directory, LAYOUT_FILE_NAME)
        self.vissim.LoadLayout(file_name)
        self.vissim.Simulation.SetAttValue('UseMaxSimSpeed', True)
        end_of_simulation = 10000
        self.vissim.Simulation.SetAttValue('SimPeriod', end_of_simulation)
        self.vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode", 1)
        self.vissim.SuspendUpdateGUI()

    def initiate_simulation(self):
        self.vissim.Simulation.RunSingleStep()

    def run_step(self):
        self.vissim.Simulation.SetAttValue("SimBreakAt", self.vissim.Simulation.AttValue('SimSec') + 2)
        self.vissim.Simulation.RunContinuous()

    def get_reward(self):
        # Create reward function
        pass
    
    def set_vehicle_input(self, amount, direction):
        self.vissim.Net.VehicleInputs.ItemByKey(direction).SetAttValue('Volume(1)', amount)

    def set_vehicle_direction(self, amount, leaving_direction, arriving_direction):
        self.vissim.Net.VehicleRoutingDecisionsStatic.ItemByKey(leaving_direction).VehRoutSta.\
            ItemByKey(2*arriving_direction).setAttValue('RelFlow(1)', amount)
    
    def get_vehicles_in_lane(self, direction, lane):
        link = self.vissim.Net.Links.ItemByKey(direction)
        vehicles = link.Lanes.ItemByKey(lane).Vehs
        return vehicles
    
    def discrete_vehicles(self, direction, lane):
        vehicles = self.get_vehicles_in_lane(direction, lane)
        discrete_vehicle_location = [0]*DISCRETE_AMOUNT
        discrete_vehicle_speed = [0]*DISCRETE_AMOUNT
        for vehicle in vehicles:
            location = vehicle.AttValue('Pos')
            discrete_location = int(location/DISCRETE_LENGTH)
            discrete_vehicle_location[discrete_location] = 1
            speed = vehicle.AttValue('Speed')
            discrete_vehicle_speed[discrete_location] = int(speed)
        return discrete_vehicle_location, discrete_vehicle_speed
    
    def set_signal_state(self, signal_group_number, state):
        signal_controller = self.vissim.Net.SignalControllers.ItemByKey(SIGNAL_CONTROL_NUMBER)
        signal_group = signal_controller.SGs.ItemByKey(signal_group_number)
        signal_group.SetAttValue("SigState", state) 
    
    def bin_to_list(self, binary):
        return [bool(binary & (1 << n)) for n in range(NUMBER_OF_LANES - 1, -1, -1)]

    def run_blank_steps(self, env, steps):
        for step in range(steps):
            self.run_step()
            env.step(False)
    
    def change_to_red(self, groups_to_red, env):
        i = 1
        for group in groups_to_red:
            if group:
                self.set_signal_state(i, 'AMBER')
            i += 1
        self.vissim.Simulation.SetAttValue("SimBreakAt", self.vissim.Simulation.AttValue('SimSec') + AMBER_TIME)
        self.vissim.Simulation.RunContinuous()
        i = 1
        for group in groups_to_red:
            if group:
                self.set_signal_state(i, 'RED')
            i += 1
        self.vissim.Simulation.SetAttValue("SimBreakAt", self.vissim.Simulation.AttValue('SimSec') + INTERPHASE_TIME)
        self.vissim.Simulation.RunContinuous()
     
    def change_to_green(self, groups_to_green, env):
        i = 1
        for group in groups_to_green:
            if group:
                self.set_signal_state(i, 'REDAMBER')
            i += 1
        self.vissim.Simulation.SetAttValue("SimBreakAt", self.vissim.Simulation.AttValue('SimSec') + REDAMBER_TIME)
        self.vissim.Simulation.RunContinuous()
        i = 1
        for group in groups_to_green:
            if group:
                self.set_signal_state(i, 'GREEN')
            i += 1
        self.vissim.Simulation.SetAttValue("SimBreakAt", self.vissim.Simulation.AttValue('SimSec') + MIN_GREEN_TIME)
        self.vissim.Simulation.RunContinuous()
    
    def change_signal_state(self, current_state, new_state, env):
        groups_to_red = phases[current_state] & ~ phases[new_state]
        groups_to_green = phases[new_state] & ~ phases[current_state]
        list_group_to_red = self.bin_to_list(groups_to_red)
        list_group_to_green = self.bin_to_list(groups_to_green)
        self.change_to_red(list_group_to_red, env)
        self.change_to_green(list_group_to_green, env)
    
    def get_current_vehicle_state(self):
        location_array = []
        speed_array = []
        for direction in range(DIRECTIONS):
            for lane in range(3):
                locations, speeds = self.discrete_vehicles(direction, lane)
                location_array.append(locations)
                speed_array.append(speeds)
        return location_array, speed_array


'''vissim.Simulation.SetAttValue('UseMaxSimSpeed', True)
End_of_simulation = 10000
vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)
vissim.Simulation.SetAttValue("SimBreakAt", vissim.Simulation.AttValue('SimSec') + 10)
vissim.Simulation.RunContinuous()

for j in range(12):
    set_signal_state(j + 1, 'RED')

vissim.Simulation.SetAttValue("SimBreakAt", vissim.Simulation.AttValue('SimSec') + 11)
vissim.Simulation.RunContinuous()

change_signal_state(13, 0)
vissim.Simulation.SetAttValue("SimBreakAt", vissim.Simulation.AttValue('SimSec') + 200)
vissim.Simulation.RunContinuous()


for i in range(13):
    change_signal_state(i, i + 1)
    vissim.Simulation.SetAttValue("SimBreakAt", vissim.Simulation.AttValue('SimSec') + 20)
    vissim.Simulation.RunContinuous()'''
vissim_prog = VissimController()

start_time = time.time()
for i in range(300):
    vissim_prog.run_step()
end_time = time.time()
print(end_time - start_time)
