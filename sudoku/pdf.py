import subprocess
from datetime import datetime
from fpdf import FPDF
from sudoku.difficulty import difficulties
from sudoku.generator import Generator as SudokuGenerator
from exceptions import ConfigurationError
from utils import batched, flatten_pdf, copy_to_clipboard

DEFAULT_COUNT = 1

class SudokuPDF(FPDF):

    def __init__(self, *args, easy=0, medium=0, hard=0, expert=0, **kwargs):
        if [d.name for d in difficulties] != ['Easy', 'Medium', 'Hard', 'Expert']:
            raise ConfigurationError('Invalid difficulty options.')

        self.difficulty_counts = [easy, medium, hard, expert]
        self.table_of_contents = True
        self.owner_page = True
        super().__init__(*args, **kwargs)

    def page_no(self):
        return super().page_no() - int(self.owner_page) - int(self.table_of_contents)

    @property
    def left_side_gutter(self):
        return self.page_no() % 2 == 0

    @property
    def left_offset(self):
        return .55 if self.left_side_gutter else .9

    @property
    def right_offset(self):
        return 5.45 if self.left_side_gutter else 5.1

    @property
    def x_center(self):
        return 2.825 if self.left_side_gutter else 3.175

    @property
    def top_offset(self):
        return 1.5

    @property
    def cell_size(self):
        return self.w / 12

    @property
    def section_size(self):
        return self.cell_size * 3

    @property
    def grid_size(self):
        return self.section_size * 3

    def footer(self):
        if self.page_no() >= 1:
            self.set_font('Montserrat', size=12)
            page_no = str(self.page_no())
            self.set_xy(self.x_center - self.get_string_width(page_no), -1.5)
            self.cell(1, 1, page_no, 0, 0, 'L')

    def draw_owner_page(self):
        self.add_page()
        line_width = 2.69
        left_offset = 1.655
        top_offset = 2
        cell_height = 0.25
        line_distance = .75
        self.set_font('Montserrat', size=12)
        self.set_line_width(0.01)
        for label in ('Owner:', 'Phone:', 'Email:'):
            self.set_xy(left_offset, top_offset)
            self.cell(line_width, cell_height, label, border='B')
            top_offset += line_distance

    def draw_table_of_contents(self):
        self.add_page()
        self.set_font('Montserrat', size=30)
        self.set_line_width(0.001)
        self.set_xy(self.left_offset, 1)
        self.cell(self.left_offset, 0, 'Table of Contents', 0, 1, 'L')

        top_offset = 2
        line_height = 1
        self.set_font('Montserrat', size=24)
        page_no = 1
        for difficulty, count in [*zip([d.name for d in difficulties], self.difficulty_counts), ('Solutions', 1)]:
            if count > 0:
                self.set_xy(self.left_offset, top_offset)
                self.cell(self.left_offset, 0, f'{page_no} · {difficulty.upper()}', 0, 1, 'L')
                top_offset += line_height
                page_no += count + 1

    def draw_chapter_page(self, title):
        self.add_page()
        self.set_font('Montserrat', size=48)
        self.set_line_width(0.001)
        self.set_xy(self.left_offset, 4)
        self.cell(self.left_offset, 0, title.upper(), 0, 1, 'L')

    def draw_boards(self, boards):
        puzzle_no = 1
        for difficulty, batch in zip(difficulties, boards):
            if not batch:
                continue

            self.draw_chapter_page(difficulty.name)
            for board in batch:
                self.add_page()
                self.draw_sudoku_grid(board, puzzle_no)
                puzzle_no += 1

    def draw_solutions(self, solutions):
        self.draw_chapter_page('Solutions')
        for batch in batched(list(enumerate(solutions, 1)), 4):
            for puzzle_no, solution in batch:
                self.add_page()
                self.draw_sudoku_grid(solution, puzzle_no)

    def draw_sudoku_grid(self, board, puzzle_no):
        self.set_font('Montserrat', size=24)
        self.set_line_width(0.001)
        self.set_xy(self.left_offset, 1)
        self.cell(self.left_offset, 0, f'No. {puzzle_no}', 0, 1, 'L')
        self.ln()

        # Draw the grid cells
        self.set_font('NunitoLight', size=16)
        grid = board.values
        for i in range(9):
            for j in range(9):
                x = j * self.cell_size + self.left_offset
                y = i * self.cell_size + self.top_offset
                self.set_xy(x, y)
                self.cell(self.cell_size, self.cell_size, str(grid[i][j]), border=1, align='C')

        # Draw thick borders
        self.set_line_width(0.05)
        self.rect(self.left_offset, self.top_offset, self.grid_size, self.grid_size)
        self.set_line_width(0.025)
        self.rect(self.left_offset, self.top_offset + self.section_size, self.grid_size, self.section_size)
        self.rect(self.left_offset + self.section_size, self.top_offset, self.section_size, self.grid_size)

        self.set_font('Montserrat')
        self.set_xy(self.left_offset, self.top_offset + self.grid_size + self.cell_size * .25)
        text = board.difficulty.name.upper() if board.difficulty else 'Solution'
        self.cell(0, self.cell_size * .5, txt=text)

    def setup_fonts(self):
        self.add_font('NunitoLight', '', 'fonts/Nunito/static/Nunito-Light.ttf', uni=True)
        self.add_font('Montserrat', '', 'fonts/Montserrat/Montserrat-VariableFont_wght.ttf', uni=True)

    def create_pdf(self):
        filename = datetime.now().strftime(f'sudoku-grids/sudoku-{"_".join([str(c) for c in self.difficulty_counts])}-%b%e-%H_%M_%S-%Y')
        filepath = f'{filename}.pdf'
        filepath_flat = f'{filename}-flat.pdf'
        self.setup_fonts()

        # Generate puzzles
        generators = [[SudokuGenerator(d) for _ in range(c)] for d, c in zip(difficulties, self.difficulty_counts)]
        boards = [[g.board for g in batch] for batch in generators]
        solutions = [g.solution for batch in generators for g in batch]

        self.draw_owner_page()
        self.add_page() # Blank page so that both owner * ToC are on the right side
        self.draw_table_of_contents()
        self.draw_boards(boards)
        self.draw_solutions(solutions)

        self.output(filepath)
        flatten_pdf(filepath, filepath_flat)
        copy_to_clipboard(filepath_flat)
