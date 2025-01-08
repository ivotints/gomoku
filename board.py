WIDTH = 1000
SIZE = 20

class coordinate:
    def __init__(self, pos): #(y, x)
        self.co = pos #(y, x)
    def __add__(self, other):
        result = []
        if isinstance(other, tuple):
            for i, j in zip(self.co, other):
                result.append(i + j)
            return tuple(result)
        if isinstance(other, coordinate):
            for i, j in zip(self.co, other.co):
                result.append(i + j)
            return tuple(result)
        return NotImplemented

    def __mul__(self, other):
        result = []
        if isinstance(other, int):
            for i in self.co:
                result.append(i * other)
            return tuple(result)
        return NotImplemented

    def __sub__(self, other):
        result = []
        if isinstance(other, tuple):
            for i, j in zip(self.co, other):
                result.append(i - j)
            return tuple(result)
        if isinstance(other, coordinate):
            for i, j in zip(self.co, other.co):
                result.append(i - j)
            return tuple(result)
        return NotImplemented

def out_of_bounds(move):
    return move[0] < 0 or move[0] >= SIZE - 1 or move[1] < 0 or move[1] >= SIZE - 1

def coord_to_bit(move):
    row, col = move
    return row * (SIZE - 1) + col

def bit_to_coord(bit):
    return divmod(bit, SIZE - 1)
