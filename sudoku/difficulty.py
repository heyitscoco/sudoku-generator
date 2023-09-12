class Difficulty():

    def __init__(self, name, logical_cutoff=35, random_cutoff=0):
        self.name = name.title()
        self.logical_cutoff = logical_cutoff
        self.random_cutoff = random_cutoff

    def __repr__(self):
        return f'<Difficulty: {self.name} ({self.logical_cutoff}, {self.random_cutoff})>'

difficulties = [
    Difficulty('Easy', 35, 0),
    Difficulty('Medium', 81, 5),
    Difficulty('Hard', 81, 10),
    Difficulty('Expert', 81, 15),
]