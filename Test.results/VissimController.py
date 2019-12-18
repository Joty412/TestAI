import os
import win32com.client as com
import numpy as np

# Inputs
NETWORK_FILE_NAME = 'Junction.inpx'
LAYOUT_FILE_NAME = 'Junction.layx'
LANE_LENGTH = 200
DISCRETE_LENGTH = 5

# Calculated Inputs
DISCRETE_AMOUNT = int(LANE_LENGTH/DISCRETE_LENGTH)

# Directions
North = 2
East = 3
South = 4
West = 1

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


Vissim.Simulation.SetAttValue("SimBreakAt", 100)
Vissim.Simulation.RunContinuous()
locations, speeds = discrete_vehicles(North, 1)
print(locations)
print(speeds)

