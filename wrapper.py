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

# Used by check_capture
class CaptureResult(ctypes.Structure):
    _fields_ = [("capture_count", ctypes.c_int),
                ("positions", ctypes.POINTER(ctypes.c_int)),
                ("position_count", ctypes.c_int)]

_lib.check_capture.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_int,
    ctypes.c_int
]
_lib.check_capture.restype = CaptureResult

_lib.is_won.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_bool,
    ctypes.c_int
]
_lib.is_won.restype = ctypes.c_bool

_lib.bot_play.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_bool,
    ctypes.POINTER(ctypes.c_int)
]
_lib.bot_play.restype = ctypes.c_int

def convert_to_array(board_int):
    # Convert 19x19 board integer to array of 19 uint32
    arr = np.zeros(19, dtype=np.uint32)
    for i in range(19):
        arr[i] = (board_int >> (i * 19)) & ((1 << 19) - 1)
    return arr

def check_capture(board_turn, board_not_turn, y, x):
    arr_turn = convert_to_array(board_turn)
    arr_not_turn = convert_to_array(board_not_turn)
    
    result = _lib.check_capture(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        y, x
    )
    
    positions = [result.positions[i] for i in range(result.position_count)]
    return result.capture_count, positions

def is_won(boards, turn, capture_opponent):
    arr_turn = convert_to_array(boards[turn][0])
    arr_not_turn = convert_to_array(boards[not turn][0])
    
    return _lib.is_won(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        turn,
        capture_opponent
    )

def bot_play(boards, turn, captures):
    arr_turn = convert_to_array(boards[turn][0])
    arr_not_turn = convert_to_array(boards[not turn][0])
    captures_arr = (ctypes.c_int * 2)(captures[0], captures[1])
    
    return _lib.bot_play(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        turn,
        captures_arr
    )