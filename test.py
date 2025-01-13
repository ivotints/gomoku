import numpy as np
from wrapper import convert_to_array, reconstruct_board

def test_board_reconstruction():
    # Create test board with a single piece
    original_board = 1 << 20  # Set bit at position 20
    
    # Convert to array and back
    arr = convert_to_array(original_board)
    reconstructed = reconstruct_board(arr)
    
    # Print for comparison
    print(f"Original:     {bin(original_board)}")
    print(f"Reconstructed: {bin(reconstructed)}")
    print(f"Equal: {original_board == reconstructed}")
    
    # Print array representation
    print("\nArray representation:")
    for i, row in enumerate(arr):
        print(f"Row {i}: {bin(row)[2:]:>19}")

test_board_reconstruction()