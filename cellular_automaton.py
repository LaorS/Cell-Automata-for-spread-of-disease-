import pygame
import random
import argparse
import matplotlib.pyplot as plt
import time
parser = argparse.ArgumentParser(description='Pandemic Simulation- Cellular Automata')
parser.add_argument('NS',type=int)
parser.add_argument('NV',type=int)
parser.add_argument('Pi',type=float)
parser.add_argument('Pv',type=float)
parser.add_argument('T',type=int)
args = parser.parse_args()
HEIGHT = 300
WIDTH = 300
POPULATION = 50000
NS = args.NS
NV = args.NV
CELL_SIZE = 2
pi = args.Pi
pv = args.Pv
T = args.T

def get_possible_positions(grid,row,col):
    """"Returns possible positions to move to given a grid and row and column indices"""
    options = []
    for i in [0, 1, -1]:
        for j in [0, 1, -1]:
            new_row = (row + i) % HEIGHT
            new_col = (col + j) % WIDTH
            if grid[new_row][new_col] is None:
                options.append((new_row, new_col))
    return options


def next_position(grid, row, col):
    """return a random next position for a person in cell i,j"""
    options = get_possible_positions(grid,row,col)
    try:
        # Try to return the next random position
        return random.choice(options)
    except:
        # if there's nowhere to move to return None
        return None


class Person:
    def __init__(self, state, row, col,T_value=T):
        self.state = state
        self.t = 0
        self.T = T_value
        self.row = row
        self.col = col
        if self.state == 'S':
            self.t = self.T

    def is_sick(self):
        return self.state == 'S'

    def update_state(self, sick_neighbors_count):
        if self.state == 'S':
            self.t -= 1
            if self.t == 0:
                self.state = 'V'
        elif self.state == 'H':
            if sick_neighbors_count > 0:
                for i in range(sick_neighbors_count):
                    if random.random() <= pi:
                        self.state = 'S'
                        self.t = self.T
                        break
        else:
            if sick_neighbors_count > 0:
                for i in range(sick_neighbors_count):
                    if random.random() <= pv:
                        self.state = 'S'
                        self.t = self.T
                        break

    def update_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        if self.state == 'S':
            return 255, 0, 0
        elif self.state == 'V':
            return 0, 255, 0
        else:
            return 0, 0, 255


def count_sick_neighbors(grid, row, col):
    count = 0
    for i in [0, 1, -1]:
        for j in [0, 1, -1]:
            if grid[(row + i) % HEIGHT][(col + j) % WIDTH]:
                if grid[(row + i) % HEIGHT][(col + j) % WIDTH].state == 'S':
                    count += 1
    return count


def update_states(grid,ppl):
    """"Update the states of each person in grid according to its neighbors"""
    for p in ppl:
        row, col = p.row, p.col
        sick_count = count_sick_neighbors(grid, row, col)
        p.update_state(sick_count)


def update(grid, ppl):
    for p in ppl:
        pos = next_position(grid,p.row,p.col)
        if pos:
            new_row,new_col = pos
            grid[new_row][new_col] = p
            grid[p.row][p.col] = None
            p.update_position(new_row,new_col)
    random.shuffle(ppl) # add randomization - each iteration people move in a different order
    return grid, ppl


def color_world(surface, grid):
    for i in range(HEIGHT):
        for j in range(WIDTH):
            color = 0, 0, 0
            if grid[i][j]:
                color = grid[i][j].get_color()
            pygame.draw.rect(surface, color, (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))


def populate():
    """The function populates the world, returns the occupied grid and a list of the people"""
    ppl = []
    grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)] # initialize the grid
    idxs = {(i, j) for i in range(HEIGHT) for j in range(WIDTH)}
    nh = POPULATION - (NS + NV) # number of healthy people
    nv_coords = random.sample(list(idxs), NV) # coordinates for the vaccinated
    idxs -= set(nv_coords)
    ns_coords = random.sample(list(idxs), NS) # coordinates for the sick
    idxs -= set(ns_coords)
    nh_coords = random.sample(list(idxs), nh) # coordinates for the healthy
    for row, col in nv_coords:
        p = Person('V', row, col)
        grid[row][col] = p
        ppl.append(p)

    for row, col in ns_coords:
        p = Person('S', row, col)
        grid[row][col] = p
        ppl.append(p)
    for row, col in nh_coords:
        p = Person('H', row, col)
        grid[row][col] = p
        ppl.append(Person('H', row, col))
    return grid, ppl


def get_sick_pctg(ppl):
    sick_count = len(list(filter(lambda x: x.state == 'S',ppl)))
    return sick_count/len(ppl)


def get_vaccinated_pctg(ppl):
    v_count = len(list(filter(lambda x: x.state == 'V',ppl)))
    return v_count/len(ppl)


def main():
    pygame.init()
    screen = pygame.display.set_mode([600, 600])
    # Run until the user asks to quit
    running = True
    grid, ppl = populate()

    sick_pctgs = []
    vaccinated_pctgs = []
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        sick_pctgs.append(get_sick_pctg(ppl))
        vaccinated_pctgs.append(get_vaccinated_pctg(ppl))
        color_world(screen, grid)
        pygame.display.update()
        update_states(grid,ppl)
        grid,ppl = update(grid, ppl)
    # Done! Time to quit.
    pygame.quit()
    plt.plot(sick_pctgs, 'r')
    plt.plot(vaccinated_pctgs, 'g')
    plt.show()

if __name__ == '__main__':
    main()
