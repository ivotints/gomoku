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

# 31 pattern and its value
PATTERN = {
    # single pieces (value 0)
    (0b00001, 0),
    (0b00010, 0),
    (0b00100, 0),
    (0b01000, 0),
    (0b10000, 0),
    
    # Pairs (value 1)
    (0b00011, 1),
    (0b00101, 1),
    (0b01001, 1),
    (0b10001, 1),
    (0b00110, 1),
    (0b01010, 1),
    (0b10010, 1),
    (0b01100, 1),
    (0b10100, 1),
    (0b11000, 1),
    
    # Threes (value 8)
    (0b00111, 8),
    (0b01011, 8),
    (0b10011, 8),
    (0b01110, 8),
    (0b10110, 8),
    (0b11100, 8),
    (0b01101, 8),
    (0b10101, 8),
    (0b11001, 8),
    (0b11010, 8),
    
    # Fours (value 64)
    (0b01111, 64),
    (0b10111, 64),
    (0b11011, 64),
    (0b11101, 64),
    (0b11110, 64),
    (0b11111, 512),
}