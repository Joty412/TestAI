import os
import win32com.client as com
import numpy as np

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

# Register Vissim COM
Vissim = com.gencache.EnsureDispatch("Vissim.Vissim")

# Load Vissim network and layout
current_directory = os.getcwd()
file_name = os.path.join(current_directory, NETWORK_FILE_NAME)
Vissim.LoadNet(file_name, False)
file_name = os.path.join(current_directory, LAYOUT_FILE_NAME)
Vissim.LoadLayout(file_name)


def set_vehicle_input(amount, direction):
    Vissim.Net.VehicleInputs.ItemByKey(direction).SetAttValue('Volume(1)', amount)


def set_vehicle_direction(amount, leaving_direction, arriving_direction):
    Vissim.Net.VehicleRoutingDecisionsStatic.ItemByKey(leaving_direction).VehRoutSta.ItemByKey(2*arriving_direction).\
        SetAttValue('RelFlow(1)', amount)


def get_vehicles_in_lane(direction, lane):
    link = Vissim.Net.Links.ItemByKey(direction)
    vehicles = link.Lanes.ItemByKey(lane).Vehs
    return vehicles


def discrete_vehicles(direction, lane):
    vehicles = get_vehicles_in_lane(direction, lane)
    discrete_vehicle_location = [0]*DISCRETE_AMOUNT
    discrete_vehicle_speed = [0]*DISCRETE_AMOUNT
    for vehicle in vehicles:
        location = vehicle.AttValue('Pos')
        discrete_location = int(location/DISCRETE_LENGTH)
        discrete_vehicle_location[discrete_location] = 1
        speed = vehicle.AttValue('Speed')
        discrete_vehicle_speed[discrete_location] = int(speed)
    return discrete_vehicle_location, discrete_vehicle_speed


def set_signal_state(signal_group_number, state):
    signal_controller = Vissim.Net.SignalControllers.ItemByKey(SIGNAL_CONTROL_NUMBER)
    signal_group = signal_controller.SGs.ItemByKey(signal_group_number)
    signal_group.SetAttValue("SigState", state)


def bin_to_list(binary):
    return [bool(binary & (1 << n)) for n in range(NUMBER_OF_LANES - 1, -1, -1)]


def change_to_red(groups_to_red):
    i = 1
    for group in groups_to_red:
        if group:
            set_signal_state(i, 'AMBER')
        i += 1
    Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + AMBER_TIME)
    Vissim.Simulation.RunContinuous()
    i = 1
    for group in groups_to_red:
        if group:
            set_signal_state(i, 'RED')
        i += 1
    Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + INTERPHASE_TIME)
    Vissim.Simulation.RunContinuous()


def change_to_green(groups_to_green):
    i = 1
    for group in groups_to_green:
        if group:
            set_signal_state(i, 'REDAMBER')
        i += 1
    Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + REDAMBER_TIME)
    Vissim.Simulation.RunContinuous()
    i = 1
    for group in groups_to_green:
        if group:
            set_signal_state(i, 'GREEN')
        i += 1
    Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + MIN_GREEN_TIME)
    Vissim.Simulation.RunContinuous()


def change_signal_state(current_state, new_state):
    groups_to_red = phases[current_state] & ~ phases[new_state]
    groups_to_green = phases[new_state] & ~ phases[current_state]
    list_group_to_red = bin_to_list(groups_to_red)
    list_group_to_green = bin_to_list(groups_to_green)
    change_to_red(list_group_to_red)
    change_to_green(list_group_to_green)


def get_current_vehicle_state():
    location_array = []
    speed_array = []
    for direction in range(DIRECTIONS):
        for lane in range(3):
            locations, speeds = (direction, lane)
            location_array.append(locations)
            speed_array.append(speeds)
    return location_array, speed_array


Vissim.Simulation.SetAttValue('UseMaxSimSpeed', True)
End_of_simulation = 10000
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)
Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + 10)
Vissim.Simulation.RunContinuous()

for j in range(12):
    set_signal_state(j + 1, 'RED')

Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + 11)
Vissim.Simulation.RunContinuous()

change_signal_state(13, 0)
Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + 200)
Vissim.Simulation.RunContinuous()


for i in range(13):
    change_signal_state(i, i + 1)
    Vissim.Simulation.SetAttValue("SimBreakAt", Vissim.Simulation.AttValue('SimSec') + 20)
    Vissim.Simulation.RunContinuous()
