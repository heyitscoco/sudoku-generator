from datetime import datetime
from fpdf import FPDF
from sudoku.difficulty import difficulties
from sudoku.generator import Generator as SudokuGenerator
from sudoku.dimensions import PDFDimensionsMixin
from exceptions import ConfigurationError
from utils import batched, flatten_pdf, copy_to_clipboard

DEFAULT_COUNT = 1


class SudokuPDF(PDFDimensionsMixin, FPDF):

    def __init__(self, *args, easy=0, medium=0, hard=0, expert=0, dimensions=None, **kwargs):
        if [d.name for d in difficulties] != ['Easy', 'Medium', 'Hard', 'Expert']:
            raise ConfigurationError('Invalid difficulty options.')
        self._difficulty_counts = [easy, medium, hard, expert]
        super().__init__(*args, **kwargs)
        self._calculate_measurements()

    def footer(self):
        if self.page_no >= 1:
            self.set_font('Montserrat', size=12)
            page_no = str(self.page_no)
            self.set_xy(self.center - self.get_string_width(page_no), -(self.width / 6))
            self.cell(1, 1, page_no, 0, 0, 'L')

    def _draw_owner_page(self):
        self.add_page()
        line_length = self.width / 1.75
        cell_height = 0.25
        left_offset = self.center - (line_length / 2)
        top_offset = self.height / 4.5
        self.set_font('Montserrat', size=12)
        self.set_line_width(0.01)
        for text in ('Owner:', 'Phone:', 'Email:'):
            self.set_xy(left_offset, top_offset)
            self.cell(line_length, cell_height, text, border='B')
            top_offset += self.line_spacing_lg

    def _draw_table_of_contents(self):
        self.add_page()
        self.set_font('Montserrat', size=30)
        self.set_line_width(0.001)
        self.set_xy(self.l_margin, self.t_margin)
        self.cell(self.l_margin, 0, 'Table of Contents', 0, 1, 'L')

        self.set_font('Montserrat', size=24)
        section_names = [*(d.name for d in difficulties), 'Solutions']
        counts = [*(c for c in self._difficulty_counts), 1]
        top_offset = self.t_margin + self.line_spacing_lg
        page_no = 1
        for section_name, count in zip(section_names, counts):
            if count > 0:
                self.set_xy(self.l_margin, top_offset)
                self.cell(self.l_margin, 0, f'{page_no} · {section_name.upper()}', 0, 1, 'L')
                top_offset += self.line_spacing_lg
                page_no += count + 1

    def _draw_chapter_page(self, title):
        self.add_page()
        self.set_font('Montserrat', size=48)
        self.set_line_width(0.001)
        self.set_xy(self.l_margin, self.height * .4)
        self.cell(self.l_margin, 0, title.upper(), 0, 1, 'L')

    def _draw_sudoku_grid(self, board, puzzle_no):
        self.set_font('Montserrat', size=24)
        self.set_line_width(0.001)
        self.set_xy(self.l_margin, self.t_margin)
        self.cell(0, 0, f'No. {puzzle_no}', 0, 1, 'L')
        self.ln()

        # Draw the grid cells
        self.set_font('NunitoLight', size=16)
        grid = board.values
        t_margin = self.t_margin + self.line_spacing_sm * 1.5
        for i in range(9):
            for j in range(9):
                x = j * self.cell_size + self.l_margin
                y = i * self.cell_size + t_margin
                self.set_xy(x, y)
                self.cell(self.cell_size, self.cell_size, str(grid[i][j]), border=1, align='C')

        # Draw thick borders
        self.set_line_width(0.05)
        self.rect(self.l_margin, t_margin, self.grid_size, self.grid_size)
        self.set_line_width(0.025)
        self.rect(self.l_margin, t_margin + self.section_size, self.grid_size, self.section_size)
        self.rect(self.l_margin + self.section_size, t_margin, self.section_size, self.grid_size)

        self.set_font('Montserrat')
        self.set_xy(self.l_margin, t_margin + self.grid_size + self.cell_size * .25)
        text = board.difficulty.name.upper() if board.difficulty else 'SOLUTION'
        self.cell(0, self.cell_size * .5, txt=text)

    def _draw_boards(self, boards):
        puzzle_no = 1
        for difficulty, batch in zip(difficulties, boards):
            if not batch:
                continue

            self._draw_chapter_page(difficulty.name)
            for board in batch:
                self.add_page()
                self._draw_sudoku_grid(board, puzzle_no)
                puzzle_no += 1

    def _draw_solutions(self, solutions):
        self._draw_chapter_page('Solutions')
        for batch in batched(list(enumerate(solutions, 1)), 4):
            for puzzle_no, solution in batch:
                self.add_page()
                self._draw_sudoku_grid(solution, puzzle_no)

    def _setup_fonts(self):
        self.add_font('NunitoLight', '', 'fonts/Nunito/static/Nunito-Light.ttf', uni=True)
        self.add_font('Montserrat', '', 'fonts/Montserrat/Montserrat-VariableFont_wght.ttf', uni=True)

    def create_pdf(self):
        difficulty_counts_string = "_".join([str(c) for c in self._difficulty_counts])
        filename = datetime.now().strftime(f'sudoku-grids/sudoku-{difficulty_counts_string}-%b%e-%H_%M_%S-%Y')
        filepath = f'{filename}.pdf'
        filepath_flat = f'{filename}-flat.pdf'
        self._setup_fonts()

        # Generate puzzles
        generators = [[SudokuGenerator(d) for _ in range(c)] for d, c in zip(difficulties, self._difficulty_counts)]
        boards = [[g.board for g in batch] for batch in generators]
        solutions = [g.solution for batch in generators for g in batch]

        self._draw_owner_page()
        self._draw_table_of_contents()
        self._draw_boards(boards)
        self._draw_solutions(solutions)

        self.output(filepath)
        flatten_pdf(filepath, filepath_flat)
        copy_to_clipboard(filepath_flat)
        print(filepath)
