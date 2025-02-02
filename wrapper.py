import ctypes
import os
import glob
import numpy as np
import atexit

lib_pattern = os.path.join(os.path.dirname(__file__), 'heuristic*.so')
lib_paths = glob.glob(lib_pattern)
if not lib_paths:
    raise RuntimeError("Could not find heuristic shared library")
_lib = ctypes.CDLL(lib_paths[0])

class CaptureResult(ctypes.Structure):
    _fields_ = [("capture_count", ctypes.c_int),
                ("positions", ctypes.POINTER(ctypes.c_int)),
                ("position_count", ctypes.c_int)]

_lib.is_won.argtypes = [
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_int
]
_lib.is_won.restype = ctypes.c_bool

class BotResult(ctypes.Structure):
    _fields_ = [("move", ctypes.c_int),
                ("evaluation", ctypes.c_int)]

_lib.bitwise_heuristic.argtypes = [
       ctypes.POINTER(ctypes.c_uint32), 
       ctypes.POINTER(ctypes.c_uint32), 
       ctypes.c_int, 
       ctypes.c_int,
   ]
_lib.bitwise_heuristic.restype = ctypes.c_int



_lib.new_bot_play.argtypes = [
    ctypes.POINTER(ctypes.c_uint32 * 19),  # boards[2][19]
    ctypes.c_bool,                         # turn
    ctypes.POINTER(ctypes.c_uint8 * 2),   # captures[2]
    ctypes.c_int                          # depth
]
_lib.new_bot_play.restype = BotResult

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

def is_won(board_turn, board_not_turn, capture_opponent):
    arr_turn = convert_to_array(board_turn)
    arr_not_turn = convert_to_array(board_not_turn)
    
    return _lib.is_won(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        capture_opponent
    )

def bot_play(boards, turn, captures, depth, last_move, search=False):
    arr_turn = convert_to_array(boards[turn][0])
    arr_not_turn = convert_to_array(boards[not turn][0])
    captures_arr = (ctypes.c_int * 2)(captures[0], captures[1])
    return _lib.bot_play(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        turn,
        captures_arr,
        depth,
        last_move,
        search
    )

def get_board_evaluation(board_turn, board_not_turn, capture_turn, capture_not_turn):
   
    from wrapper import convert_to_array
    arr_turn = convert_to_array(board_turn)
    arr_not_turn = convert_to_array(board_not_turn)
    
    return _lib.bitwise_heuristic(
        arr_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        arr_not_turn.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
        capture_turn,
        capture_not_turn
    )

def new_bot_play(boards, turn, captures, depth):
    arr_boards = ((ctypes.c_uint32 * 19) * 2)()
    for i in range(2):
        board_arr = convert_to_array(boards[i][0])
        for j in range(19):
            arr_boards[i][j] = board_arr[j]
            
    captures_arr = (ctypes.c_uint8 * 2)()
    captures_arr[0] = captures[0]
    captures_arr[1] = captures[1]
    return _lib.new_bot_play(
        arr_boards,
        turn,
        ctypes.byref(captures_arr), 
        depth
    )

_lib.initializeZobristTable.argtypes = []
_lib.initializeZobristTable.restype = None
_lib.init_global_tables.argtypes = []
_lib.init_global_tables.restype = None


_lib.cleanup_global_tables.argtypes = []
_lib.cleanup_global_tables.restype = None

atexit.register(lambda: _lib.cleanup_global_tables())

def initialize_bot():
    _lib.initializeZobristTable()
    _lib.init_global_tables()
