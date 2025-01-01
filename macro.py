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
    (0b10101, 5),
    (0b010110, 6),
    (0b011010, 6)
}

PAIR_PATTERNS = {
    0b11000,
    0b01100,
    0b00110,
    0b00011,
    0b10100,
    0b01010,
    0b00101,
    0b10010,
    0b01001,
    0b10001
}

THREE_PATTERNS = [
    0b11100,
    0b01110,
    0b00111,
    0b11010,
    0b01101,
    0b10110,
    0b01011,
    0b11001,
    0b10011,
    0b10101,
]

FOUR_PATTERNS = [
    0b11110,
    0b11101,
    0b11011,
    0b10111,
    0b01111,
]
