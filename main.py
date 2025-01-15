import os
import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame as py
import pygame.draw as pyd
from render import draw_board, update_board, draw_suggestion, show_winning_message
from game import handle_move, is_occupied
import argparse
import copy
import time
from wrapper import bot_play
from macro import SIZE, WIDTH
BLACK_PLAYER = 0
WHITE_PLAYER = 1

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

        py.display.set_caption("Gomoku")
        draw_board(self.win)
        py.display.update()



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

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("--player", "-p", type=int, choices=[1, 2], help="Choose amount of player 1 or 2", nargs='?', default=1)
    args = parse.parse_args()
    with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
        py.init()
    game = gomoku(args.player - 1)
    while game.running:
        if not game.thinking:
            for event in py.event.get():
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        game.running = False
                if event.type == py.QUIT:
                    game.running = False
                if event.type == py.MOUSEBUTTONDOWN:
                    pos = find_mouse_pos(py.mouse.get_pos())
                    # print("mouse pos:", pos)
                    if pos is None:
                        continue
                    move = pos[1] * 19 + pos[0]
                    if not is_occupied(game.boards[BLACK_PLAYER], (pos[1], pos[0])) and not is_occupied(game.boards[WHITE_PLAYER], (pos[1], pos[0])):
                        # we go here after mouse click and if it was not occupied
                        # turn is 0 for now because it is black's turn
                        result, has_capture = handle_move(game.boards, game.turn, move, game.captures)
                        legal = handle_turn(game, result)
                        # turn is 1
                        if legal and not game.solo:
                            game.thinking = True
                            start = time.time()
                            # turn is 1
                            # move, game.eval = bot_play(game.boards, game.turn, copy.deepcopy(game.captures))
                            bot_result = bot_play(game.boards, game.turn, copy.deepcopy(game.captures))
                            move = bot_result.move
                            game.eval = -bot_result.evaluation
                            result, has_capture = handle_move(game.boards, game.turn, move, game.captures)
                            handle_turn(game, result)
                            print(f"Time taken: {time.time() - start:.2f}")
                            game.thinking = False
                            draw_suggestion(game, bot_play(game.boards, game.turn, copy.deepcopy(game.captures)))

if __name__ == '__main__':
    main()

