# Name: Forest fire's simulation
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import math
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np

INITIAL_CHAPARRAL_FUEL = 0.7
INITIAL_LAKE_FUEL = 0
INITIAL_FOREST_FUEL = 0.8
INITIAL_CANYON_FUEL = 0.9
INITIAL_TOWN_FUEL = 0.9

WIND_DIRECTION = "N"
WIND_CONSTANT = 2



def transition_func(grid, neighbourstates, neighbourcounts, fuel_resources):
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Forest fire simulation"
    config.dimensions = 2
    config.states = (0, 1, 2)
    config.test = "test"
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0,0.50,0),(1,0,0),(0,0,0)]
    config.num_generations = 500
    config.grid_dims = (500,500)
    config.initial_grid = np.zeros((500,500))

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    # Create resource array
    fuel_resources = initialise_fuel()

    # Create grid object
    grid = Grid2D(config, (transition_func, fuel_resources))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


def cell_resource(x,y):
    if x >= 100 and x <= 150 and y >=50 and y<=150:
        return 1
    elif x >= 300 and x <= 400 and y >= 150 and y <= 250:
        return 2
    elif x >= 50 and x <= 350 and y >= 325 and y <= 350:
        return 3
    elif x >= 470 and y >= 0 and y <= 25:
        return 4
    return 0


def initialise_fuel():
    resources = np.zeros((500, 500))
    for x in range(0, 500):
        for y in range(0, 500):
            cell_type = cell_resource(x,y)
            if cell_type == 0:
                resources[x][y] = INITIAL_CHAPARRAL_FUEL
            elif cell_type == 1:
                resources[x][y] = INITIAL_LAKE_FUEL
            elif cell_type == 2:
                resources[x][y] = INITIAL_FOREST_FUEL
            elif cell_type == 3:
                resources[x][y] = INITIAL_CANYON_FUEL
            elif cell_type == 4:
                resources[x][y] = INITIAL_TOWN_FUEL
    return resources


def get_wind_effect(direction):
    dsin = round(WIND_CONSTANT*math.sin(45), 2)
    if direction == "N":
        return dsin, WIND_CONSTANT, dsin, 1, 1, 1, 1, 1
    elif direction == "S":
        return 1, 1, 1, 1, 1, dsin, WIND_CONSTANT, dsin
    elif direction == "W":
        return dsin, 1, 1, WIND_CONSTANT, 1, dsin, 1, 1
    elif direction == "E":
        return 1, 1, dsin, 1, WIND_CONSTANT, 1, 1, dsin
    elif direction == "NW":
        return WIND_CONSTANT, dsin, 1, dsin, 1, 1, 1, 1
    elif direction == "NE":
        return 1, dsin, WIND_CONSTANT, 1, dsin, 1, 1, 1
    elif direction == "SW":
        return 1, 1, 1, dsin, 1, WIND_CONSTANT, dsin, 1
    elif direction == "SE":
        return 1, 1, 1, 1, dsin, 1, dsin, WIND_CONSTANT


def get_wind_adjustment(angle, base_angle):
    return round(abs((base_angle - angle) / 90), 2)


if __name__ == "__main__":
    main()
