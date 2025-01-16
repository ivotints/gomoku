import os
import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame as py
from render import draw_board, update_board, draw_suggestion, show_winning_message, display_time
from game import handle_move, is_occupied
import argparse
import copy
import time
from wrapper import bot_play
from macro import SIZE, WIDTH
BLACK_PLAYER = 0
WHITE_PLAYER = 1

class Move:
    def __init__(self, game):
        self.boards = [game.boards[0].copy(), game.boards[1].copy()]
        self.turn = game.turn
        self.captures = game.captures.copy()
        self.eval = game.eval
        self.time = game.time

class gomoku:
    def __init__(self, players):
        self.boards = [[0], [0]] # its working in reverse direction. if our map is 3 by 3 and in pos 0, 0 is 1 than int looks like 0b000000001
        self.turn = BLACK_PLAYER
        self.win = py.display.set_mode((WIDTH, WIDTH))
        self.captures = [0, 0]
        self.running = True
        self.solo = players
        self.thinking = False
        self.eval = 0
        self.show_suggestions = False
        self.time = 0
        self.history = []

        py.init()
        py.display.set_caption("Gomoku")
        draw_board(self.win)
        py.display.update()

    def save_move(self):
        """Save current game state to history"""
        self.history.append(Move(self))
    
    def undo_move(self):
        """Restore previous game state from history"""
        if not self.history:
            return False
        
        previous = self.history.pop()
        self.boards = [previous.boards[0].copy(), previous.boards[1].copy()]
        self.turn = previous.turn
        self.captures = previous.captures.copy()
        self.eval = previous.eval
        self.time = previous.time
        update_board(self)
        return True

def find_mouse_pos(pos):
    x, y = pos
    w = WIDTH / SIZE
    if x < w - w / 3 or x > WIDTH - w + w / 3 or y < w - w / 3 or y > WIDTH - w + w / 3:
        return None
    x = round(x / w)
    y = round(y / w)
    return ((x - 1, y - 1))


def handle_turn(game, result):
    if result is None:
        return False
    game.save_move()
    update_board(game)
    game.turn = not game.turn
    
    if result:
        show_winning_message(game)
    return True

def handle_user_move(game, pos):
    """Handle a user's mouse click to make a move"""
    if pos is None:
        return False
        
    move = pos[1] * 19 + pos[0]
    if not is_occupied(game.boards[0], move) and not is_occupied(game.boards[1], move):
        result, has_capture = handle_move(game.boards, game.turn, move, game.captures)
        return handle_turn(game, result)
    return False

def handle_bot_move(game):
    """Handle the bot's turn"""
    game.thinking = True
    start = time.time()
    
    # Get and execute bot's move
    bot_result = bot_play(game.boards, game.turn, copy.deepcopy(game.captures))
    move = bot_result.move
    game.eval = -bot_result.evaluation
    result, has_capture = handle_move(game.boards, game.turn, move, game.captures)

    game.time = time.time() - start
    handle_turn(game, result)
    game.thinking = False

def handle_events(game):
    """Handle pygame events"""
    for event in py.event.get():
        if event.type in (py.QUIT, py.KEYDOWN):
            if event.type == py.KEYDOWN and event.key != py.K_ESCAPE:
                continue
            game.running = False
            return False
            
        if event.type == py.MOUSEBUTTONDOWN:
            pos = find_mouse_pos(py.mouse.get_pos())
            if handle_user_move(game, pos) and not game.solo:
                handle_bot_move(game)
    return True

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("--player", "-p", type=int, choices=[1, 2], 
                      help="Choose amount of player 1 or 2", nargs='?', default=1)
    parse.add_argument("--suggest", "-s", action="store_true", 
                      help="Show move suggestions", default=False)
    args = parse.parse_args()
        
    game = gomoku(args.player - 1)
    game.show_suggestions = args.suggest
    
    while game.running:
        if not game.thinking:
            handle_events(game)

if __name__ == '__main__':
    main()

