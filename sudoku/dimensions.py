DEFAULT_DIMENSIONS = {
    (4, 6): {
        'font_size_sm': 8,
        'contact_line_length': 2.5,
        'line_spacing_lg': .75,
    },
}


def get(key, *dicts, default=None):
    for d in dicts:
        val = d.get(key)
        if val is not None:
            return val
    return default


def round_if_int(val):
    return int(val) if int(val) == val else val


class PDFDimensionsMixin():

    def _calculate_measurements(self):
        # Horizontal margin constraints based on KDP rules: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6#margins
        dimensions = DEFAULT_DIMENSIONS.get((self.width, self.height)) or {}
        _small_margin = dimensions.get('small_margin') or max(.25, self.width / 16)
        _large_margin = dimensions.get('large_margin') or max(.5, self.width / 10)
        _top_margin = dimensions.get('top_margin') or (self.width / 6)

        self._even_page_margins = {
            'left': _small_margin,
            'right': _large_margin,
            'top': _top_margin,
        }
        self._odd_page_margins = {
            'left': _large_margin,
            'right': _small_margin,
            'top': _top_margin,
        }
        self._font_size_sm = dimensions.get('font_size_sm') or 12                               # contact, footer
        self._font_size_md = dimensions.get('font_size_md') or max(0, self.font_size_sm * 1.5)  # sudoku cells
        self._font_size_lg = dimensions.get('font_size_lg') or max(0, self.font_size_md * 1.5)  # ToC chapters, puzzle #
        self._font_size_xl = dimensions.get('font_size_xl') or max(0, self.font_size_lg * 1.5)  # ToC title, chapters

        self._contact_line_length = dimensions.get('contact_line_length') or max(self.width / 3.35, 2.5)
        self._contact_cell_height = dimensions.get('contact_cell_height') or .25

        self._line_spacing_lg = dimensions.get('line_spacing_lg') or (self.width / 8)
        self._line_spacing_sm = dimensions.get('line_spacing_sm') or (self.line_spacing_lg / 3)

        self._line_width_sm = dimensions.get('line_width_sm') or .001
        self._cell_size = dimensions.get('cell_size') or (self.width / 12)

    @property
    def width(self):
        return round_if_int(self.fw)

    @property
    def height(self):
        return round_if_int(self.fh)

    @property
    def content_width(self):
        return self.width - self.l_margin - self.r_margin

    @property
    def center(self):
        return self.l_margin + self.content_width / 2

    @property
    def font_size_sm(self):
        return self._font_size_sm

    @property
    def font_size_md(self):
        return self._font_size_md

    @property
    def font_size_lg(self):
        return self._font_size_lg

    @property
    def font_size_xl(self):
        return self._font_size_xl

    @property
    def line_spacing_sm(self):
        return self._line_spacing_sm

    @property
    def line_width_sm(self):
        return self._line_width_sm

    @property
    def line_spacing_lg(self):
        return self._line_spacing_lg

    @property
    def cell_size(self):
        return self._cell_size

    @property
    def section_size(self):
        return self.cell_size * 3

    @property
    def grid_size(self):
        return self.section_size * 3

    @property
    def contact_line_length(self):
        return self._contact_line_length

    @property
    def contact_cell_height(self):
        return self._contact_cell_height

    @property
    def page_no(self):
        # Account for owner page & table of contents
        return super().page_no() - 2

    def add_page(self):
        super().add_page()
        self.update_margins()

    def update_margins(self):
        margins = self._even_page_margins if self.even_page() else self._odd_page_margins
        self.set_margins(**margins)

    def even_page(self):
        return self.page_no % 2 == 0
