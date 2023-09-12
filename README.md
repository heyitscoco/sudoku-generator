# Overview
This is a tool for generating sudoku books, based on Paul Rutledge's original sudoku implementation. The original code has been extended so that it can generate PDF manuscripts with puzzles of varying difficulty.

The final product has several features that make it suitable for uploading to KDP or other platforms:
- It produces a fully flattened PDF.
- Each page is slightly offset, so that they'll look properly centered once the gutter is applied.
- An owner page is included by default.

<img width="255" alt="Owner page screenshot" src="https://github.com/heyitscoco/sudoku-generator/assets/10701968/1dfe5951-f648-48c0-aa27-b56fd4d69511">

<img width="255" alt="Easy sudoku screenshot" src="https://github.com/heyitscoco/sudoku-generator/assets/10701968/161f2392-a6db-4c6e-8379-3fb32864e064">

<img width="255" alt="Medium sudoku screenshot" src="https://github.com/heyitscoco/sudoku-generator/assets/10701968/2b281808-63b6-4a81-af48-234477ab9fee">


# Setup
```bash
# Create and activate the virtual environment of your choice
virtualenv env && source env/bin/activate

# Install dependencies
make install
```

# Usage

```bash
# Creates 25 easy, 25 medium, 25 hard, 25 expert
python main.py --count 100

# Creates 100 easy, 25 medium
python main.py --easy 100 --medium 50
```

# Limitations & Future Improvements
- If the `--count` option is used with a value that isn't divisible by 4, it will create fewer puzzles than requested. (Ex., `--count 10` will create 2 puzzles of each type, or 8 in total.)
- It can only create 6"x9" manuscripts.
- It doesn't include answer keys.
- The puzzles are always in order of difficulty; there's no way to randomize the order.
