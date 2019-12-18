import os
# COM-Server
import win32com.client as com

## Connecting the COM Server => Open a new Vissim Window:
Vissim = com.gencache.EnsureDispatch("Vissim.Vissim") #
# Vissim = com.Dispatch("Vissim.Vissim") # once the cache has been generated, its faster to call Dispatch which also creates the connection to Vissim.
# If you have installed multiple Vissim Versions, you can open a specific Vissim version adding the version number
# Vissim = com.gencache.EnsureDispatch("Vissim.Vissim.10") # Vissim 10
# Vissim = com.gencache.EnsureDispatch("Vissim.Vissim.11") # Vissim 11


### for advanced users, with this command you can get all Constants from PTV Vissim with this command (not required for the example)
##import sys
##Constants = sys.modules[sys.modules[Vissim.__module__].__package__].constants

Path_of_COM_Basic_Commands_network = os.getcwd() #'C:\\Users\\Public\\Documents\\PTV Vision\\PTV Vissim 11\\Examples Training\\COM\\Basic Commands\\'

## Load a Vissim Network:
Filename = os.path.join(Path_of_COM_Basic_Commands_network, 'Test.inpx')
flag_read_additionally = False # you can read network(elements) additionally, in this case set "flag_read_additionally" to true
Vissim.LoadNet(Filename, flag_read_additionally)

## Load a Layout:
Filename = os.path.join(Path_of_COM_Basic_Commands_network, 'Test.layx')
Vissim.LoadLayout(Filename)

Vissim.Simulation.SetAttValue('UseMaxSimSpeed', True)
End_of_simulation = 1000  # simulation second [s]
Vissim.Simulation.SetAttValue('SimPeriod', End_of_simulation)

# Set vehicle input:
VI_number   = 1 # VI = Vehicle Input
new_volume  = 600 # vehicles per hour
Vissim.Net.VehicleInputs.ItemByKey(VI_number).SetAttValue('Volume(1)', new_volume)

Sim_break_at = 20 # simulation second [s]
Vissim.Simulation.SetAttValue("SimBreakAt", Sim_break_at)
Vissim.Simulation.RunContinuous()

SC_number = 1 # SC = SignalController
SG_number = 1 # SG = SignalGroup
SignalController = Vissim.Net.SignalControllers.ItemByKey(SC_number)
SignalGroup = SignalController.SGs.ItemByKey(SG_number)
new_state = "RED" # possible values 'GREEN', 'RED', 'AMBER', 'REDAMBER' and more, see COM Help: SignalizationState Enumeration
SignalGroup.SetAttValue("SigState", new_state)

Sim_break_at = 50 # simulation second [s]
Vissim.Simulation.SetAttValue("SimBreakAt", Sim_break_at)
Vissim.Simulation.RunContinuous()

link_number = 4
link = Vissim.Net.Links.ItemByKey(link_number)
print(link.Vehs.GetMultiAttValues("QTime"))


new_state = "GREEN" # possible values 'GREEN', 'RED', 'AMBER', 'REDAMBER' and more, see COM Help: SignalizationState Enumeration
SignalGroup.SetAttValue("SigState", new_state)

Vissim.Simulation.RunContinuous()
