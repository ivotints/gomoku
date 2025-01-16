import os
import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame as py
from render import draw_board, update_board, show_winning_message
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
        self.is_multiplayer = players
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
        print(f"\n=== Saving Move ===")
        print(f"Current boards: {self.boards}")
        print(f"Current turn: {'Black' if self.turn == 0 else 'White'}")
        print(f"Current captures: {self.captures}")
        print(f"Current eval: {self.eval}")
        self.history.append(Move(self))
        print(f"History length after save: {len(self.history)}")

    def undo_move(self):
        """Restore previous game state from history"""
        print(f"\n=== Attempting Undo ===")
        if not self.history:
            print("No moves in history to undo")
            return False
        
        print(f"Current state before undo:")
        print(f"Boards: {self.boards}")
        print(f"Turn: {'Black' if self.turn == 0 else 'White'}")
        print(f"Captures: {self.captures}")
        
        previous = self.history.pop()
        print(f"\nRestoring to previous state:")
        print(f"Previous boards: {previous.boards}")
        print(f"Previous captures: {previous.captures}")
        
        self.boards = [previous.boards[0].copy(), previous.boards[1].copy()]
        self.captures = previous.captures.copy()
        self.eval = previous.eval
        self.time = previous.time
        self.turn = not self.turn  # This line might be the issue - double turn change

        print(f"\nFinal state after undo:")
        print(f"Boards: {self.boards}")
        print(f"Turn: {'Black' if self.turn == 0 else 'White'}")
        print(f"Captures: {self.captures}")
        print(f"History length: {len(self.history)}")
        
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
        result, has_capture = handle_move(game, game.boards, game.turn, move, game.captures)
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
    result, has_capture = handle_move(game, game.boards, game.turn, move, game.captures)

    game.time = time.time() - start
    handle_turn(game, result)
    game.thinking = False



def handle_undo(game, pos):
    """Check if click position is within UNDO text bounds"""
    x, y = pos
    if (WIDTH - 50 <= x <= WIDTH - 10 and WIDTH - 25 <= y <= WIDTH - 10):
        if not game.is_multiplayer:
            if game.undo_move():
                game.undo_move()
                game.turn = not game.turn
                update_board(game)
                game.turn = not game.turn
                return True
            else:
                if game.undo_move():
                    return True
    return False
def handle_suggestion(game, pos):
    """Check if click position is within SUGGEST text bounds"""
    x, y = pos
    if (774 <= x <= 795 and 0 <= y <= 34):
        game.show_suggestions = not game.show_suggestions
        update_board(game, game.show_suggestions)
        return True
    return False

def handle_events(game):
    """Handle pygame events"""
    for event in py.event.get():
        if event.type in (py.QUIT, py.KEYDOWN):
            if event.type == py.KEYDOWN and event.key != py.K_ESCAPE:
                continue
            game.running = False
            return False
        
        if event.type == py.MOUSEBUTTONDOWN:
            click_pos = py.mouse.get_pos()
            
            if handle_suggestion(game, click_pos) or handle_undo(game, click_pos):
                return True

            pos = find_mouse_pos(click_pos)
            if handle_user_move(game, pos):
                if not game.is_multiplayer:
                    handle_bot_move(game)
                return True
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

