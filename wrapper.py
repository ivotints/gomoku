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
_lib.bitwise_heuristic.restype = ctypes.c_int

# Add to existing argtypes definitions
_lib.generate_legal_moves.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),  # board_turn
    ctypes.POINTER(ctypes.c_uint32),  # board_not_turn
    ctypes.c_int,                     # capture
    ctypes.POINTER(ctypes.c_int),     # moves array
    ctypes.POINTER(ctypes.c_int)      # move count
]
_lib.generate_legal_moves.restype = None


# Add to existing argtypes definitions
class CaptureResult(ctypes.Structure):
    _fields_ = [("capture_count", ctypes.c_int),
                ("positions", ctypes.POINTER(ctypes.c_int)),
                ("position_count", ctypes.c_int)]

_lib.check_capture_cpp.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_int,
    ctypes.c_int
]
_lib.check_capture_cpp.restype = CaptureResult

_lib.is_won_cpp.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),  # board_turn
    ctypes.POINTER(ctypes.c_uint32),  # board_not_turn
    ctypes.c_int,                     # turn
    ctypes.c_int                      # capture_opponent
]
_lib.is_won_cpp.restype = ctypes.c_bool

# Add to existing type definitions
_lib.minimax_cpp.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),  # board_turn
    ctypes.POINTER(ctypes.c_uint32),  # board_not_turn
    ctypes.c_int,                     # depth
    ctypes.c_int,                     # alpha
    ctypes.c_int,                     # beta
    ctypes.c_bool,                    # maximizing_player
    ctypes.c_int,                     # turn
    ctypes.POINTER(ctypes.c_int)      # captures
]
_lib.minimax_cpp.restype = ctypes.c_int

class MinimaxResult(ctypes.Structure):
    _fields_ = [("value", ctypes.c_int),
                ("best_move", ctypes.c_int)]


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

def generate_legal_moves_cpp(board_turn, board_not_turn, capture):
    arr_turn = convert_to_array(board_turn)
    arr_not_turn = convert_to_array(board_not_turn)
    
    moves = (ctypes.c_int * (19*19))()  # Max possible moves
    move_count = ctypes.c_int(0)
    
    _lib.generate_legal_moves(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        capture,
        moves,
        ctypes.byref(move_count)
    )
    
    return [moves[i] for i in range(move_count.value)]

def check_capture(board_turn, board_not_turn, y, x):
    arr_turn = convert_to_array(board_turn)
    arr_not_turn = convert_to_array(board_not_turn)
    
    result = _lib.check_capture_cpp(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        y, x
    )
    
    positions = [result.positions[i] for i in range(result.position_count)]
    return result.capture_count, positions

def is_won(boards, turn, capture_opponent):
    arr_turn = convert_to_array(boards[turn][0])
    arr_not_turn = convert_to_array(boards[not turn][0])
    
    return _lib.is_won_cpp(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        turn,
        capture_opponent
    )

def minimax(boards, depth, alpha, beta, maximizing_player, turn, captures):
    arr_turn = convert_to_array(boards[turn][0])
    arr_not_turn = convert_to_array(boards[not turn][0])
    captures_arr = (ctypes.c_int * 2)(captures[0], captures[1])
    
    return _lib.minimax_cpp(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        depth, alpha, beta, maximizing_player, turn,
        captures_arr
    )
