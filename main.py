import argparse

from sudoku.pdf import SudokuPDF
from sudoku.difficulty import difficulties


class SudokuArgumentParser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()
        self.add_argument('--count', type=int, nargs='?', help='The total number of puzzles to include.')
        for d in difficulties:
            name = d.name.lower()
            self.add_argument(f'--{name}', type=int, default=0, help=f'The number of {name} puzzles to include.')

    def parse_args(self):
        args = super().parse_args().__dict__
        count = args.pop('count', None)
        if count:
            group_size = round(count / 4)
            args['easy'] = args['medium'] = args['hard'] = args['expert'] = group_size
        return args


if __name__ == '__main__':
    args = SudokuArgumentParser().parse_args()
    print(args)
    SudokuPDF(unit='in', format=(4, 6), **args).create_pdf()
    SudokuPDF(unit='in', format=(6, 9), **args).create_pdf()
