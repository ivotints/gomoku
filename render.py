import pygame.draw as pyd
import pygame as py
from macro import BLACK, WHITE, WIDTH, SIZE
from wrapper import get_board_evaluation, bot_play, new_bot_play
import math
import time

def draw_undo_button(win):
    font = py.font.Font(None, 20)
    text = font.render("UNDO", True, BLACK)
    text_rect = text.get_rect()
    
    text_rect.bottomright = (WIDTH - 10, WIDTH - 10)
    win.blit(text, text_rect)

def get_average_time(game):
    if not game.history:
        return 0
        
    # Filter only moves where time > 0 (bot moves)
    bot_times = [move.time for move in game.history if move.time > 0]
    if not bot_times:
        return 0
        
    return sum(bot_times) / len(bot_times)

def display_time(game, current_time):
    font = py.font.Font(None, 24)
    
    current_elapsed = time.time() - current_time
    
    time_text = f"Time: {current_elapsed:.2f}"
    text = font.render(time_text, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH//2 - 60, WIDTH - 20))
    game.win.blit(text, text_rect)
    
    if game.thinking:
        times = [move.time for move in game.history if move.time > 0]
        times.append(current_elapsed)
        avg_time = sum(times) / len(times) if times else 0
    else:
        avg_time = get_average_time(game)
        
    avg_text = f"Avg: {avg_time:.2f}"
    avg = font.render(avg_text, True, BLACK)
    avg_rect = avg.get_rect(center=(WIDTH//2 + 60, WIDTH - 20))
    game.win.blit(avg, avg_rect)

def show_winning_message(game):
    is_black_winner = game.turn
    message = "Black wins!" if is_black_winner else "White wins!"
    
    text_color = (0, 0, 0) if is_black_winner else (255, 255, 255)
    border_color = (255, 255, 255) if is_black_winner else (0, 0, 0)
    
    font = py.font.Font(None, 74)
    
    border_offsets = [(x, y) for x in (-2, 2) for y in (-2, 2)]
    for offset_x, offset_y in border_offsets:
        border_text = font.render(message, True, border_color)
        border_rect = border_text.get_rect(center=(WIDTH // 2 + offset_x, WIDTH // 2 + offset_y))
        game.win.blit(border_text, border_rect)
    
    text = font.render(message, True, text_color)
    text_rect = text.get_rect(center=(WIDTH // 2, WIDTH // 2))
    game.win.blit(text, text_rect)
    
    py.display.update()
    py.time.wait(4000)
    exit(0)


def draw_suggestion(game, suggested_move):
    move = suggested_move.move
    x = move % 19
    y = move // 19
    pyd.circle(game.win, (128,128,128), 
              ((x + 1) * WIDTH / SIZE, (y + 1) * WIDTH / SIZE), 
              WIDTH / SIZE / 3, 2)


def draw_board(win, captures=[0, 0], evaluation=0):
    win.fill((235,173,100))
    square = WIDTH / SIZE
    
    for i in range(1, SIZE):
        pyd.line(win, BLACK, (i * square, square), (i * square, WIDTH - square), width=2)
        pyd.line(win, BLACK, (square, i * square), (WIDTH - square, i * square), width=2)
    
    font = py.font.Font(None, 24)
    text = font.render(f"Captures:     {captures[0]}", True, BLACK)
    text_rect = text.get_rect(center=(80, 20))
    win.blit(text, text_rect)
    text = font.render(str(captures[1]), True, WHITE)
    text_rect = text.get_rect(center=(180, 20))
    win.blit(text, text_rect)
    
    draw_suggestion_button(win)
    bar_width = 15
    bar_height = WIDTH - 2 * square
    bar_x = square/2 - bar_width/2
    bar_y = square
    
    pyd.rect(win, (200,200,200), (bar_x, bar_y + 1, bar_width, bar_height))
    
    if evaluation != 0:
        sign = 1 if evaluation > 0 else -1
        log_eval = sign * math.log(abs(evaluation) + 1, 10)
        fill_ratio = min(max(log_eval / 4, -1), 1)
        
        center_y = bar_y + bar_height/2 + 1
        if evaluation > 0:
            fill_WIDTH = fill_ratio * bar_height/2
            fill_y = center_y - fill_WIDTH
        else:
            fill_WIDTH = -fill_ratio * bar_height/2
            fill_y = center_y
            
        color = BLACK if evaluation > 0 else WHITE
        pyd.rect(win, color, (bar_x, fill_y, bar_width, abs(fill_WIDTH)))
    
    pyd.line(win, BLACK, (bar_x, bar_y + bar_height/2), 
             (bar_x + bar_width - 1, bar_y + bar_height/2), width=2)

def draw_suggestion_button(win):
    font = py.font.Font(None, 50)
    text = font.render('?', False, BLACK)
    text_rect = text.get_rect()
    
    text_rect.topright = (WIDTH - 5, 5)
    win.blit(text, text_rect)

def update_board(game, sugg=False):
    draw_board(game.win, game.captures, game.eval if not game.is_multiplayer else get_board_evaluation(game.boards[0][0], game.boards[1][0], game.captures[0], game.captures[1]))
    draw_undo_button(game.win)
    color = [BLACK, WHITE]
    if not game.is_multiplayer:
        display_time(game, time.time() - game.time)

    for player, board in enumerate(game.boards):
        b = board.copy()
        pos = 0
        while b[0]:
            if b[0] & 1:
                x = pos % (SIZE - 1)
                y = pos // (SIZE - 1)

                px = (x + 1) * WIDTH / SIZE
                pyy = (y + 1) * WIDTH / SIZE
                pyd.circle(game.win, color[player], (px, pyy), WIDTH / SIZE / 3)
                if pos == game.last_move:
                    pyd.circle(game.win, (0, 180,0), (px, pyy), WIDTH / SIZE / 3, 2)
            b[0] >>= 1
            pos += 1
    if (game.show_suggestions and (game.is_multiplayer or not game.is_white == game.turn)) or sugg:
        turn = game.is_white if sugg else not game.turn
        draw_suggestion(game, new_bot_play(game.boards, turn, game.captures, 4))
    py.display.update()