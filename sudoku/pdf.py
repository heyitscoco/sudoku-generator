import subprocess
from datetime import datetime
from fpdf import FPDF
from pdf2image import convert_from_path
from sudoku.difficulty import difficulties
from sudoku.generator import Generator as SudokuGenerator
from exceptions import ConfigurationError

DEFAULT_COUNT = 1



def copy_to_clipboard(data):
    subprocess.run("pbcopy", text=True, input=data)


def flatten_pdf(input_pdf_path, output_pdf_path, dpi=400, resolution=400.0):
    images = convert_from_path(input_pdf_path, dpi=dpi)
    im1 = images[0]
    images.pop(0)
    im1.save(output_pdf_path, "PDF", resolution=resolution, save_all=True, append_images=images)


class SudokuPDF(FPDF):

    def __init__(self, *args, owner_page=True, easy=0, medium=0, hard=0, expert=0, **kwargs):
        if [d.name for d in difficulties] != ['Easy', 'Medium', 'Hard', 'Expert']:
            raise ConfigurationError('Invalid difficulty options.')

        self.difficulty_counts = [easy, medium, hard, expert]
        self.owner_page = owner_page
        super().__init__(*args, **kwargs)

    @property
    def puzzle_no(self):
        return self.page_no() - int(self.owner_page)

    @property
    def left_side_gutter(self):
        return self.page_no() % 2 == 0

    @property
    def x_offset(self):
        return .55 if self.left_side_gutter else .9

    @property
    def y_offset(self):
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

    def draw_owner_page(self):
        line_width = 2.69
        x_offset = 1.655
        y_offset = 2
        cell_height = 0.25
        line_distance = .75
        self.set_font('NunitoLight', size=12)
        for label in ('Owner:', 'Phone:', 'Email:'):
            self.set_xy(x_offset, y_offset)
            self.cell(line_width, cell_height, label, border='B')
            y_offset += line_distance

    def draw_sudoku_grid(self, board):
        self.set_font('Montserrat', size=24)
        self.set_line_width(0.001)
        self.set_xy(self.x_offset, 1)
        self.cell(self.x_offset, 0, f'No. {self.puzzle_no}', 0, 1, 'L')
        self.ln()

        # Draw the grid cells
        self.set_font('NunitoLight', size=16)
        grid = board.values
        for i in range(9):
            for j in range(9):
                x = j * self.cell_size + self.x_offset
                y = i * self.cell_size + self.y_offset
                self.set_xy(x, y)
                self.cell(self.cell_size, self.cell_size, str(grid[i][j]), border=1, align='C')

        # Draw thick borders
        self.set_line_width(0.05)
        self.rect(self.x_offset, self.y_offset, self.grid_size, self.grid_size)
        self.set_line_width(0.025)
        self.rect(self.x_offset, self.y_offset + self.section_size, self.grid_size, self.section_size)
        self.rect(self.x_offset + self.section_size, self.y_offset, self.section_size, self.grid_size)

        self.set_font('Montserrat')
        self.set_xy(self.x_offset, self.y_offset + self.grid_size + self.cell_size * .25)
        self.cell(0, self.cell_size * .5, txt=board.difficulty.name.upper())

    def setup_fonts(self):
        self.add_font('NunitoLight', '', 'fonts/Nunito/static/Nunito-Light.ttf', uni=True)
        self.add_font('Montserrat', '', 'fonts/Montserrat/Montserrat-VariableFont_wght.ttf', uni=True)

    def create_pdf(self, flatten=False):
        filename = datetime.now().strftime(f'sudoku-grids/sudoku-{"_".join([str(c) for c in self.difficulty_counts])}-%b%e-%H_%M_%S-%Y')
        filepath = f'{filename}.pdf'
        filepath_flat = f'{filename}-flat.pdf'
        self.setup_fonts()

        # Owner Page
        self.add_page()
        self.draw_owner_page()

        # Puzzle Pages
        for difficulty, count in zip(difficulties, self.difficulty_counts):
            for _ in range(count):
                self.add_page()
                generator = SudokuGenerator(difficulty)
                self.draw_sudoku_grid(generator.board)
        self.output(filepath)

        # Flattened File
        if flatten:
            flatten_pdf(filepath, filepath_flat)
            copy_to_clipboard(filepath_flat)
        else:
            copy_to_clipboard(filepath)
