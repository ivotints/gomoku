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