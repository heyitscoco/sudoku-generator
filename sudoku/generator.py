import random
from functools import reduce

from .board import Board
from .solver import Solver


BASE_FILE = 'base.txt'

class Generator:

    # constructor for generator, reads in a space delimited
    def __init__(self, difficulty):
        # Instantiate the starting board
        with open(BASE_FILE) as f:
            # reducing file to a list of numbers
            numbers = filter(lambda x: x in '123456789', list(reduce(lambda x, y: x + y, f.readlines())))
            numbers = list(map(int, numbers))

        # constructing board
        self.board = Board(numbers)
        self.solution = self.board.copy()
        self._populate_board(difficulty)

    def _populate_board(self, difficulty):
        self.board.difficulty = difficulty
        # applying random transformations to the finished puzzle
        self._randomize(100)
        # Use difficulty cutoffs to apply logical & random reduction
        self._reduce_via_logical(difficulty.logical_cutoff)
        if difficulty.random_cutoff:
            self._reduce_via_random(difficulty.random_cutoff)
        return self.board

    # function randomizes an existing complete puzzle
    def _randomize(self, iterations):

        # not allowing transformations on a partial puzzle
        if len(self.board.get_used_cells()) != 81:
            raise ValueError('Rearranging partial board may compromise uniqueness.')

        # looping through iterations
        for x in range(0, iterations):

            # to get a random column/row
            case = random.randint(0, 4)

            # to get a random band/stack
            block = random.randint(0, 2) * 3

            # in order to select which row and column we shuffle an array of
            # indices and take both elements
            piece1, piece2 = random.sample([0, 1, 2], 2)

            # pick case according to random to do transformation
            if case == 0:
                self.board.swap_row(block + piece1, block + piece2)
            elif case == 1:
                self.board.swap_column(block + piece1, block + piece2)
            elif case == 2:
                self.board.swap_stack(piece1, piece2)
            elif case == 3:
                self.board.swap_band(piece1, piece2)      

        assert Solver(self.board).is_valid(), f'Invalid Sudoku board!\n{self.board}'

    # method gets all possible values for a particular cell, if there is only one
    # then we can remove that cell
    def _reduce_via_logical(self, cutoff=81):
        cells = self.board.get_used_cells()
        random.shuffle(cells)
        for cell in cells:
            if len(self.board.get_possibles(cell)) == 1:
                cell.value = 0
                cutoff -= 1
            if cutoff == 0:
                break

    # method attempts to remove a cell and checks that solution is still unique
    def _reduce_via_random(self, cutoff=81):
        temp = self.board
        existing = temp.get_used_cells()

        # sorting used cells by density heuristic, highest to lowest
        new_set = [(x, self.board.get_density(x)) for x in existing]
        elements = [x[0] for x in sorted(new_set, key=lambda x: x[1], reverse=True)]

        # for each cell in sorted list
        for cell in elements:
            original = cell.value

            # get list of other values to try in its place
            complement = [x for x in range(1, 10) if x != original]
            ambiguous = False

            # check each value in list of other possibilities to try
            for x in complement:

                # set cell to value
                cell.value = x

                # create instance of solver
                s = Solver(temp)

                # if solver can fill every box and the solution is valid then
                # puzzle becomes ambiguous after removing particular cell, so we can break out
                if s.solve() and s.is_valid():
                    cell.value = original
                    ambiguous = True
                    break

            # if every value was checked and puzzle remains unique, we can remove it
            if not ambiguous:
                cell.value = 0
                cutoff -= 1

            # if we ever meet the cutoff limit we can break out
            if cutoff == 0:
                break

    # Unused. Returns current state of generator including number of
    # empty cells and a representation of the puzzle
    def get_current_state(self):
        return (
            f'There are currently {len(self.board.get_used_cells())} starting cells.\n\r'
            f'Current puzzle state:\n\r\n\r{self.board.__str__()}\n\r'
        )
