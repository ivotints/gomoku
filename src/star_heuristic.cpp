#include "gomoku.hpp"
#define BLACK 0
#define WHITE 1



// takes a new boards, to which move will be made.
inline void make_a_move(uint32_t (&new_boards)[2][19], bool turn, uint8_t (&new_captures)[2], uint8_t y, uint8_t x, uint8_t &capture_dir)
{
    new_boards[turn][y] |= 1 << x; // set bit

    const uint8_t DIR_NW = 1 << 0; // North-West
    const uint8_t DIR_N =  1 << 1; // North
    const uint8_t DIR_NE = 1 << 2; // North-East
    const uint8_t DIR_E =  1 << 3; // East
    const uint8_t DIR_SE = 1 << 4; // South-East
    const uint8_t DIR_S =  1 << 5; // South
    const uint8_t DIR_SW = 1 << 6; // South-West
    const uint8_t DIR_W =  1 << 7; // West

    uint8_t directions = 0;  // We will assign here directions that we will explore for capture
    
    if (y >= 3)
        if (y <= 15)
            if (x >= 3)
                if (x <= 15)
                    directions = DIR_NW | DIR_N | DIR_NE | DIR_E | DIR_SE | DIR_S | DIR_SW | DIR_W; // Center area
                else 
                    directions = DIR_NW | DIR_N | DIR_SW | DIR_S | DIR_W; // Right edge
            else
                directions = DIR_N | DIR_NE | DIR_E | DIR_SE | DIR_S; // Left edge
        else
            if (x >= 3)
                if (x <= 15)
                    directions = DIR_NW | DIR_N | DIR_NE | DIR_E | DIR_W; // Bottom edge, middle x
                else
                    directions = DIR_NW | DIR_N | DIR_W; // Bottom-right corner
            else
                directions = DIR_N | DIR_NE | DIR_E; // Bottom-left corner
    else
        if (x >= 3)
            if (x <= 15)
                directions = DIR_E | DIR_SE | DIR_S | DIR_SW | DIR_W; // Top edge, middle x
            else 
                directions = DIR_SW | DIR_S | DIR_W; // Top-right corner
        else
            directions = DIR_E | DIR_SE | DIR_S; // Top-left corner

    const uint8_t dir_vect[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}}; //y, x

    for (uint8_t dir_index = 0; dir_index < 8; ++dir_index)
    {
        if (directions & (1 << dir_index)) // check if that direction exist
        {
            if (((new_boards[ turn][y + 3 * dir_vect[dir_index][0]] >> (x + 3 * dir_vect[dir_index][1])) & 1) && 
                ((new_boards[!turn][y + 2 * dir_vect[dir_index][0]] >> (x + 2 * dir_vect[dir_index][1])) & 1) && 
                ((new_boards[!turn][y +     dir_vect[dir_index][0]] >> (x +     dir_vect[dir_index][1])) & 1))
            {
                new_boards[!turn][y + 2 * dir_vect[dir_index][0]] &= ~(1 << (x + 2 * dir_vect[dir_index][1])); // if we here, mean that it is a capture.
                new_boards[!turn][y +     dir_vect[dir_index][0]] &= ~(1 << (x +     dir_vect[dir_index][1]));
                capture_dir |= (1 << dir_index);
                new_captures[turn]++;
            }
        }
    }
}

inline int evaluate_line(uint32_t black_bits, uint32_t white_bits, int length) {
    int delta = 0;
    for (int shift = 0; shift <= length - 5; ++shift) {
        uint32_t black_window = (black_bits >> shift) & 0b11111;
        uint32_t white_window = (white_bits >> shift) & 0b11111;

        if (!white_window) { // If the window has no White stones, evaluate Black stones
            int bits = __builtin_popcount(black_window);
            if (bits > 1) delta += (1 << (3 * (bits - 2)));
        }

        if (!black_window) { // If the window has no Black stones, evaluate White stones
            int bits = __builtin_popcount(white_window);
            if (bits > 1) delta -= (1 << (3 * (bits - 2)));
        }
    }
    return delta;
}

// it will output evaluation of the segment, with the center in that coordinates.
inline int star_eval(uint32_t (&boards)[2][19], int y, int x) {
    int left = std::min(4, x);
    int right = std::min(4, 18 - x);
    int up = std::min(4, y);
    int down = std::min(4, 18 - y);

    // Horizontal evaluation
    int start_x = x - left;
    int length_h = left + right + 1;    
    uint32_t black_bits_h = (boards[BLACK][y] << start_x) & ((1 << length_h) - 1);
    uint32_t white_bits_h = (boards[WHITE][y] << start_x) & ((1 << length_h) - 1);
    int value = evaluate_line(black_bits_h, white_bits_h, length_h);

    // Vertical evaluation
    int start_y = y - up;
    int length_v = up + down + 1;
    int black_bits_v = 0;
    int white_bits_v = 0;
    for(int i = 0; i < length_v; ++i)
    {
        black_bits_v |= ((boards[BLACK][start_y + i] >> x) & 1) << i;
        white_bits_v |= ((boards[WHITE][start_y + i] >> x) & 1) << i;
    }
    value += evaluate_line(black_bits_v, white_bits_v, length_v);

    // Diagonal (Top-Left to Bottom-Right) evaluation
    int diag_up = std::min(left, up);
    int diag_down = std::min(right, down);
    int start_diag_y = y - diag_up;
    int start_diag_x = x - diag_up;
    int length_d = diag_up + diag_down + 1;

    int black_bits_d = 0;
    int white_bits_d = 0;

    for(int i = 0; i < length_d; ++i)
    {
        black_bits_d |= ((boards[BLACK][start_diag_y + i] >> (start_diag_x + i)) & 1) << i;
        white_bits_d |= ((boards[WHITE][start_diag_y + i] >> (start_diag_x + i)) & 1) << i;
    }
    value += evaluate_line(black_bits_d, white_bits_d, length_d);

    // Anti-Diagonal
    int anti_up = std::min(right, up);
    int anti_down = std::min(left, down);
    int start_anti_y = y - anti_up;
    int start_anti_x = x + anti_up;

    int black_bits_a = 0;
    int white_bits_a = 0;

    for(int i = 0; i < length_d; ++i)
    {
        black_bits_a |= ((boards[BLACK][start_anti_y + i] >> (start_anti_x - i)) & 1) << i;
        white_bits_a |= ((boards[WHITE][start_anti_y + i] >> (start_anti_x - i)) & 1) << i;
    }
    value += evaluate_line(black_bits_a, white_bits_a, length_d);

    return value;
}

/*
    i have heuristic. Now i should implement minimax algorithm, write a bot_play function.
    Bot_play will return (best_move, evaluation_of_best_move)
    after we got the move, we will have to make it and to rewrite current_board_evaluation.
    then player makes a move. We run star heuristic on it just to get current_board_evaluatio for the bot_play.

*/

int star_heuristic(uint32_t (&boards)[2][19], bool turn, uint8_t (&captures)[2], uint8_t y, uint8_t x, int eval)
{
    uint32_t new_boards[2][19];
    uint8_t new_captures[2] = {captures[0], captures[1]};

    // copy of boards
    for(int i = 0; i < 2; ++i) {
        for(int j = 0; j < 19; ++j) {
            new_boards[i][j] = boards[i][j];
        }
    }

    uint8_t capture_dir = 0; // each bit will represent direction of capture was made

    make_a_move(new_boards, turn, new_captures, y, x, capture_dir);

    const uint8_t dir_vect[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}}; //y, x
    for (uint8_t dir_index = 0; dir_index < 8; ++dir_index)
    {
        if (capture_dir & (1 << dir_index)) // check capture
        {
            // if we have a capture, we will run an additional star heuristics on each capture_pos.
            int old_eval = star_eval(boards, y + 2 * dir_vect[dir_index][0], x + 2 * dir_vect[dir_index][1]);
            old_eval += star_eval(boards, y + dir_vect[dir_index][0], x + dir_vect[dir_index][1]);
            int new_eval = star_eval(new_boards, y + 2 * dir_vect[dir_index][0], x + 2 * dir_vect[dir_index][1]);
            new_eval += star_eval(new_boards, y + dir_vect[dir_index][0], x + dir_vect[dir_index][1]);
            int delta_eval = new_eval - old_eval;
            eval += delta_eval;
        }
    }
    if (capture_dir)
    {
        int old_capture_eval = 16 << captures[turn];
        int new_capture_eval = 16 << new_captures[turn];
        int delta_captures_eval = new_capture_eval - old_capture_eval; // what if now not the black turn? should we minus that?
        if (turn == BLACK)
            eval += delta_captures_eval;
        else 
            eval -= delta_captures_eval;
    }
    // now we need function to evaluate old board
    int old_eval = star_eval(boards, y, x);
    int new_eval = star_eval(new_boards, y, x);
    int delta_eval = new_eval - old_eval;
    eval += delta_eval; // this is new evaluation of the board.
    return (eval);
}









