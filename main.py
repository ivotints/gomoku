import pygame as py
import pygame.draw as pyd
from macro import BLACK, WHITE
from render import draw_board, update_board, find_mouse_pos
from board import coordinate, SIZE, WIDTH
from game import handle_move, is_occupied
import argparse
from ai import bot_play
import copy

class gomoku:
    def __init__(self, players):
        self.boards = [[0], [0]]
        self.turn = 0
        self.win = py.display.set_mode((WIDTH, WIDTH))
        self.captures = [0, 0]
        self.running = True
        self.solo = players
        self.thinking = False

        py.display.set_caption("Gomoku")
        draw_board(self.win)
        py.display.update()

def handle_turn(game, result, update, move):
    if result is None:
        return False
    if result:
        message = "You {}!".format("win" if not game.turn else "lose")
        font = py.font.Font(None, 74)
        text = font.render(message, True, (30, 30, 30))
        text_rect = text.get_rect(center=(WIDTH // 2, WIDTH // 2))
        game.win.blit(text, text_rect)
        print("GG")
        py.display.update()
        py.time.wait(500)  # Wait for 0.5 seconds
        exit(0)
    if update:
        update_board(game.boards, game.win)
    else:
        pyd.circle(game.win, BLACK if not game.turn else WHITE, ((move.co[1] + 1) * WIDTH / SIZE , (move.co[0] + 1) * WIDTH / SIZE), WIDTH / SIZE / 3)
    game.turn = not game.turn
    py.display.update()
    return True

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("player", type=int, choices=[1, 2], help="Choose amount of player 1 or 2", nargs='?', default=1)
    args = parse.parse_args()
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
                    if pos is None:
                        continue
                    move = coordinate((pos[1], pos[0]))
                    if not is_occupied(game.boards[0], move.co) and not is_occupied(game.boards[1], move.co):
                        result, update = handle_move(game.boards, game.turn, move, game.captures)
                        legal = handle_turn(game, result, update, move)
                        if legal and not game.solo:
                            game.thinking = True
                            move = bot_play(game.boards, game.turn, copy.deepcopy(game.captures))
                            result, update = handle_move(game.boards, game.turn, move, game.captures)
                            handle_turn(game, result, update, move)
                            game.thinking = False

if __name__ == '__main__':
    main()

