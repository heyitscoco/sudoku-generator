# !/usr/bin/python
import argparse
from Sudoku.Generator import *

DEFAULT_BASE_FILE = 'base.txt'

# setting difficulties and their cutoffs for each solve method
difficulties = {
    'easy': (35, 0), 
    'medium': (81, 5), 
    'hard': (81, 10), 
    'extreme': (81, 15)
}

def main(difficulty, base=DEFAULT_BASE_FILE):
    # constructing generator object from puzzle file (space delimited columns, line delimited rows)
    difficulty = difficulties[difficulty]
    gen = Generator(base)

    # applying 100 random transformations to puzzle
    gen.randomize(100)

    # getting a copy before slots are removed
    initial = gen.board.copy()

    # applying logical reduction with corresponding difficulty cutoff
    gen.reduce_via_logical(difficulty[0])

    # catching zero case
    if difficulty[1] != 0:
        # applying random reduction with corresponding difficulty cutoff
        gen.reduce_via_random(difficulty[1])


    # getting copy after reductions are completed
    final = gen.board.copy()

    # printing out complete board (solution)
    print("The initial board before removals was: \r\n\r\n{0}".format(initial))

    # printing out board after reduction
    print("The generated board after removals was: \r\n\r\n{0}".format(final))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('difficulty', choices=difficulties.keys())
    parser.add_argument('--base', default=DEFAULT_BASE_FILE, help='Path to a base puzzle file (space delimited columns, line delimited rows)')
    args = parser.parse_args()
    main(**args.__dict__)
