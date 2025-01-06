import os
import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame as py
import pygame.draw as pyd
from macro import BLACK, WHITE
from render import draw_board, update_board, find_mouse_pos
from board import coordinate, SIZE, WIDTH
from game import handle_move, is_occupied
import argparse
from ai import bot_play
import copy
import time
BLACK_PLAYER = 0
WHITE_PLAYER = 1

class gomoku:
    def __init__(self, players):
        #100
        #000
        #000
        # will be encoded like 0b000000001
        self.boards = [[0], [0]] # its working in reverse direction. if our map is 3 by 3 and in pos 0, 0 is 1 than int looks like 0b000000001
        self.turn = BLACK_PLAYER
        self.win = py.display.set_mode((WIDTH, WIDTH))
        self.captures = [0, 0]
        self.running = True
        self.solo = players
        self.thinking = False

        py.display.set_caption("Gomoku")
        draw_board(self.win)
        py.display.update()

def handle_turn(game, is_win, has_capture, move):
    # draw a circle on the board
    pyd.circle(game.win, BLACK if not game.turn else WHITE, ((move % 19 + 1) * WIDTH / SIZE, (move // 19 + 1) * WIDTH / SIZE), WIDTH / SIZE / 3)
    if is_win is None:
        return False
    if has_capture:
        update_board(game.boards, game.win)
    if is_win:
        message = "{} win!".format("Black" if not game.turn else "White")
        font = py.font.Font(None, 74)
        text = font.render(message, True, (30, 30, 30))
        text_rect = text.get_rect(center=(WIDTH // 2, WIDTH // 2))
        game.win.blit(text, text_rect)
        print("GG")
        py.display.update()
        py.time.wait(1000)  # Wait for 1 second
        exit(0)
    game.turn = not game.turn
    py.display.update()
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
                    pos = find_mouse_pos(py.mouse.get_pos()) #(x, y) from 0 to 18
                    # print("mouse pos:", pos)
                    if pos is None:
                        continue
                    move = pos[1] * 19 + pos[0]
                    if not is_occupied(game.boards[BLACK_PLAYER], (pos[1], pos[0])) and not is_occupied(game.boards[WHITE_PLAYER], (pos[1], pos[0])):
                        # we go here after mouse click and if it was not occupied
                        # turn is 0 for now because it is black's turn
                        is_win, has_capture = handle_move(game.boards, game.turn, move, game.captures)
                        legal = handle_turn(game, is_win, has_capture, move)
                        # turn is 1
                        if legal and not game.solo:
                            game.thinking = True
                            start = time.time()
                            # turn is 1
                            move = bot_play(game.boards, game.turn, copy.deepcopy(game.captures))

                            result, update = handle_move(game.boards, game.turn, move, game.captures)

                            handle_turn(game, result, update, move)

                            print(f"Time taken: {time.time() - start:.2f}")
                            game.thinking = False

if __name__ == '__main__':
    main()

