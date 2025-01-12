import ctypes
import os
import glob
import numpy as np

# Find the .so file
lib_pattern = os.path.join(os.path.dirname(__file__), 'heuristic*.so')
lib_paths = glob.glob(lib_pattern)
if not lib_paths:
    raise RuntimeError("Could not find heuristic shared library")
_lib = ctypes.CDLL(lib_paths[0])
_lib.bitwise_heuristic.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_int,
    ctypes.c_int
]
_lib.bitwise_heuristic.restype = ctypes.c_double


def convert_to_array(board_int):
    # Convert 19x19 board integer to array of 19 uint32
    arr = np.zeros(19, dtype=np.uint32)
    for i in range(19):
        arr[i] = (board_int >> (i * 19)) & ((1 << 19) - 1)
    return arr

def heuristic(board_turn, board_not_turn, capture, capture_opponent):
    arr_turn = convert_to_array(board_turn)
    arr_not_turn = convert_to_array(board_not_turn)
    
    return _lib.bitwise_heuristic(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        capture,
        capture_opponent
    )