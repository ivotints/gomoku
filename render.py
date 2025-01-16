import pygame.draw as pyd
import pygame as py
from macro import BLACK, WHITE, WIDTH, SIZE
from wrapper import get_board_evaluation,bot_play
import math
import copy
import time

def draw_undo_button(win):
    """Draw undo text button in right corner"""
    font = py.font.Font(None, 20)  # Smaller font size
    text = font.render("UNDO", True, BLACK)
    text_rect = text.get_rect()
    
    # Position in right corner
    text_rect.bottomright = (WIDTH - 10, WIDTH - 10)  # 10px padding from edges
    
    # Draw just the text
    win.blit(text, text_rect)

def display_time(game, start):
    """Display the time taken to make a move"""
    time_taken = time.time() - start
    font = py.font.Font(None, 24)
    text = font.render(f"Time taken: {time_taken:.2f}", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, WIDTH - 20))
    game.win.blit(text, text_rect)
    

def show_winning_message(game):
    """Display the winning message with bordered text based on winner color"""
    is_black_winner = game.turn
    message = "Black wins!" if is_black_winner else "White wins!"
    
    # Set colors based on winner
    text_color = (0, 0, 0) if is_black_winner else (255, 255, 255)
    border_color = (255, 255, 255) if is_black_winner else (0, 0, 0)
    
    font = py.font.Font(None, 74)
    
    # Create border by rendering text multiple times with offset
    border_offsets = [(x, y) for x in (-2, 2) for y in (-2, 2)]
    for offset_x, offset_y in border_offsets:
        border_text = font.render(message, True, border_color)
        border_rect = border_text.get_rect(center=(WIDTH // 2 + offset_x, WIDTH // 2 + offset_y))
        game.win.blit(border_text, border_rect)
    
    # Render main text
    text = font.render(message, True, text_color)
    text_rect = text.get_rect(center=(WIDTH // 2, WIDTH // 2))
    game.win.blit(text, text_rect)
    
    py.display.update()
    py.time.wait(2000)  # Wait for 2 seconds
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
    
    # Draw board grid
    for i in range(1, SIZE):
        pyd.line(win, BLACK, (i * square, square), (i * square, WIDTH - square), width=2)
        pyd.line(win, BLACK, (square, i * square), (WIDTH - square, i * square), width=2)
    
    # Draw captures
    font = py.font.Font(None, 24)
    text = font.render(f"Captures:     {captures[0]}", True, BLACK)
    text_rect = text.get_rect(center=(80, 20))
    win.blit(text, text_rect)
    text = font.render(str(captures[1]), True, WHITE)
    text_rect = text.get_rect(center=(180, 20))
    win.blit(text, text_rect)
    
    # Draw evaluation bar
    bar_width = 15
    bar_height = WIDTH - 2 * square
    bar_x = square/2 - bar_width/2
    bar_y = square
    
    # Draw background bar
    pyd.rect(win, (200,200,200), (bar_x, bar_y + 1, bar_width, bar_height))
    
    # Calculate bar fill using logarithmic scale
    if evaluation != 0:
        sign = 1 if evaluation > 0 else -1
        log_eval = sign * math.log(abs(evaluation) + 1, 10)
        fill_ratio = min(max(log_eval / 4, -1), 1)
        
        # Center point is middle of bar
        center_y = bar_y + bar_height/2 + 1
        if evaluation > 0:  # Black winning - fill up
            fill_WIDTH = fill_ratio * bar_height/2
            fill_y = center_y - fill_WIDTH
        else:  # White winning - fill down
            fill_WIDTH = -fill_ratio * bar_height/2
            fill_y = center_y
            
        color = BLACK if evaluation > 0 else WHITE
        pyd.rect(win, color, (bar_x, fill_y, bar_width, abs(fill_WIDTH)))
    
    # Draw center line
    pyd.line(win, BLACK, (bar_x, bar_y + bar_height/2), 
             (bar_x + bar_width - 1, bar_y + bar_height/2), width=2)



def update_board(game):
    draw_board(game.win, game.captures, game.eval if not game.is_multiplayer else get_board_evaluation(game.boards[0][0], game.boards[1][0], game.captures[0], game.captures[1]))
    draw_undo_button(game.win)
    if game.show_suggestions and ((not game.is_multiplayer and game.turn == 1) or game.is_multiplayer):
        draw_suggestion(game, bot_play(game.boards, not game.turn, copy.deepcopy(game.captures)))

    if not game.is_multiplayer:
        display_time(game, time.time()- game.time)

    for player, board in enumerate(game.boards):
        b = board.copy()
        pos = 0
        while b[0]:
            if b[0] & 1:

                x = pos % (SIZE - 1)
                y = pos // (SIZE - 1)

                px = (x + 1) * WIDTH / SIZE
                pyy = (y + 1) * WIDTH / SIZE
                color = (0, 0, 0) if player == 0 else (255, 255, 255)
                pyd.circle(game.win, color, (px, pyy), WIDTH / SIZE / 3)
            b[0] >>= 1
            pos += 1
    py.display.update()