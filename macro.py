from board import coordinate

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DIRECTIONS = [
    coordinate((0, 1)),  
    coordinate((1, 0)),  
    coordinate((1, 1)),  
    coordinate((1, -1)), 
    coordinate((0, -1)), 
    coordinate((-1, 0)), 
    coordinate((-1, -1)),
    coordinate((-1, 1))  
]

DIRECTION_MIN = [
    coordinate((0, 1)),  
    coordinate((1, 0)),  
    coordinate((1, 1)),  
    coordinate((1, -1)),
]
THREE = {
    (0b01110, 5),
    (0b010110, 6),
    (0b011010, 6)
}


PAIR_PATTERNS = {
    (0b11000, 5),
    (0b01100, 5),
    (0b00110, 5),
    (0b00011, 5),
    (0b10100, 5),
    (0b01010, 5),
    (0b00101, 5),
    (0b10010, 5),
    (0b01001, 5),
    (0b10001, 5)
}

THREE_PATTERNS = [
    (0b11100, 5),
    (0b01110, 5),
    (0b00111, 5),
    (0b11010, 5),
    (0b01101, 5),
    (0b10110, 5),
    (0b01011, 5),
    (0b11001, 5),
    (0b10011, 5),
    (0b10101, 5),
]

FOUR_PATTERNS = [
    (0b11110, 5),
    (0b11101, 5),
    (0b11011, 5),
    (0b10111, 5),
    (0b01111, 5),
]

FIVE_PATTERN = [
    (0b11111, 5),
]
