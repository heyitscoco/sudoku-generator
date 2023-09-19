DEFAULT_DIMENSIONS = {
    (4, 6): {

    },
    (6, 9): {

    }
}


class PDFDimensionsMixin():

    def _calculate_measurements(self):
        top_margin = self.width / 6
        # Constraints based on KDP rules: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6#margins
        small_margin = max(.25, self.width / 16)
        large_margin = max(.5, self.width / 11)

        self._even_page_margins = {
            'left': small_margin,
            'right': large_margin,
            'top': top_margin,
        }
        self._odd_page_margins = {
            'left': large_margin,
            'right': small_margin,
            'top': top_margin,
        }
        self._line_spacing_lg = self.width / 8
        self._line_spacing_sm = self.line_spacing_lg / 3
        self._cell_size = self.w / 12

    @property
    def width(self):
        return self.fw

    @property
    def height(self):
        return self.fh

    @property
    def content_width(self):
        return self.width - self.l_margin - self.r_margin

    @property
    def center(self):
        return self.l_margin + self.content_width / 2

    @property
    def line_spacing_sm(self):
        return self._line_spacing_sm

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
