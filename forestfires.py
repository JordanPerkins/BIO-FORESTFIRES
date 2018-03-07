# Name: Forest fire's simulation
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import math
import random
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


# INCINERATOR OR PLANT
STARTING_POSITION = "PLANT"
# N, NE E, S, SE, W, SW, NW
WIND_DIRECTION = "N"
# NUMBER OF GENERATIONS. 1 GEN = 16 seconds
NUM_GENERATIONS = 500

INITIAL_CHAPARRAL_FUEL = 1800
INITIAL_FOREST_FUEL = 3600
INITIAL_CANYON_FUEL = 900

CHAPARRAL_IGNITION = 0.075
FOREST_IGNITION = -0.55
SCRUBLAND_IGNITION = 0.5

PROBABILITY_CONSTANT = 0.29

WATER_DROP_GENERATION = -1
WATER_DROP_COORDS = []


def transition_func(grid, neighbourstates, neighbourcounts, fuel_resources, water, generation):
    for x in range (0, 500):
        for y in range (0,500):
            if WATER_DROP_GENERATION != -1:
                if water[x][y] > 0:
                    if neighbourcounts[1][x][y] == 0:
                        water[x][y] = water[x][y] - 587
                    elif neighbourcounts[1][x][y] < 4:
                        water[x][y] = water[x][y] - 1176
                    else:
                        water[x][y] = water[x][y] - 2352
            if grid[x][y] == 1:
                fuel_resources[x][y] = fuel_resources[x][y] - 16
                if fuel_resources[x][y] <= 0:
                    grid[x][y] = 2
            elif grid[x][y] == 0:
                if light_cell(x, y, neighbourstates, water, generation[0]):
                    grid[x][y] = 1
            if generation[0] == WATER_DROP_GENERATION:
                putout = cell_putout(generation[0], x, y)
                water[x][y] = 570000*putout[0]
                if putout[1]:
                    grid[x][y] = 0

    generation[0] =+ 1
    return grid


def light_cell(x, y, neighbourstates, water, generation):
    ignition = cell_ignition(x, y)
    if ignition == 0:
        return False
    wind = wind_effect(WIND_DIRECTION)
    probability = random.random()
    for cell in range (0,8):
        if neighbourstates[cell][x][y] == 1:
            prob = PROBABILITY_CONSTANT*(1+ignition)*wind[cell]
            if WATER_DROP_GENERATION != -1:
                water_factor = 1-(water[x][y]/570000)
                water_neighbours = neighbour_waterstates(water, x, y)
                damp_factor = 1-(water_neighbours[cell]/570000)
                prob = prob*water_factor*damp_factor
            if prob >= probability:
                return True
    return False


def cell_putout(generation, x, y):
    time = (generation * 16) / 3600
    rand = random.random()
    type = cell_resource(x, y)
    if type == 0:
        if time < 1:
            if 0.5 > rand:
                return 0.5*rand, True
            else:
                return 0.5*rand, False
        else:
            if 0.3 > rand:
                return 0.3*rand, True
            else:
                return 0.3*rand, False
    elif type == 2:
        if time < 2:
            if 0.8 > rand:
                return 0.8*rand, True
            else:
                return 0.8*rand, False
        else:
            if 0.4 > rand:
                return 0.4*rand, True
            else:
                return 0.4*rand, False
    elif type == 3:
        if 0.3 > rand:
            return 0.3*rand, True
        else:
            return 0.3*rand, False
    return 0, False


def neighbour_waterstates(water, x, y):
    return water[x-1][y-1], water[x-1][y], water[x-1][y+1], water[x][y-1], water[x][y+1], water[x+1][y-1], water[x+1][y], water[x+1][y+1]


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
    config.num_generations = NUM_GENERATIONS
    config.grid_dims = (500,500)
    grid = np.zeros((500,500))

    # Set starting position
    if STARTING_POSITION == "INCINERATOR":
      grid[0][499] = 1
    elif STARTING_POSITION == "PLANT":
      grid[0][0] = 1

    config.initial_grid = grid
    config.wrap = False

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

    # Create water array
    if WATER_DROP_GENERATION != -1:
      water = initialise_water()
    else:
      water = None

    generation = [0]

    # Create grid object
    grid = Grid2D(config, (transition_func, fuel_resources, water, generation))

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
                resources[x][y] = -1
            elif cell_type == 2:
                resources[x][y] = INITIAL_FOREST_FUEL
            elif cell_type == 3:
                resources[x][y] = INITIAL_CANYON_FUEL
            elif cell_type == 4:
                resources[x][y] = -1
    return resources


def initialise_water():
    water = np.zeros((500, 500))
    for x in range(0, 500):
        for y in range(0, 500):
            if [x,y] in WATER_DROP_COORDS:
                water[x][y] = 570000
    return water


def cell_ignition(x,y):
    cell_type = cell_resource(x,y)
    if cell_type == 0:
        return CHAPARRAL_IGNITION
    elif cell_type == 2:
        return FOREST_IGNITION
    elif cell_type == 3:
        return INITIAL_CANYON_FUEL
    return 0


def wind_effect(direction):
    dsin = round(math.sin(45), 2)
    if direction == "N":
        return dsin, 0.5, dsin, 0.5, 0.5, 0.5, 0.5, 0.5
    elif direction == "S":
        return 0.5, 0.5, 0.5, 0.5, 0.5, dsin, 1, dsin
    elif direction == "W":
        return dsin, 0.5, 0.5, 1, 0.5, dsin, 0.5, 0.5
    elif direction == "E":
        return 0.5, 0.5, dsin, 0.5, 1, 0.5, 0.5, dsin
    elif direction == "NW":
        return 1, dsin, 0.5, dsin, 0.5, 0.5, 0.5, 0.5
    elif direction == "NE":
        return 0.5, dsin, 1, 0.5, dsin, 0.5, 0.5, 0.5
    elif direction == "SW":
        return 0.5, 0.5, 0.5, dsin, 0.5, 1, dsin, 0.5
    elif direction == "SE":
        return 0.5, 0.5, 0.5, 0.5, dsin, 0.5, dsin, 1



if __name__ == "__main__":
    main()
