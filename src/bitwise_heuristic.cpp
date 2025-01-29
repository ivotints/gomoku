#include "gomoku.hpp"

inline void evaluate_line(uint32_t black_bits, uint32_t white_bits, int length, int &value) {
    for (int shift = 0; shift <= length - 5; ++shift) {
        uint32_t black_window = (black_bits >> shift) & 0b11111;
        uint32_t white_window = (white_bits >> shift) & 0b11111;

        if (!white_window) { // If the window has no White stones, evaluate Black stones
            int bits = __builtin_popcount(black_window);
            if (bits > 1) 
            {
                value += (1 << (3 * (bits - 2)));
                if (bits == 5 && value < 100'000) // not to give the reward twice.
                    value += 1'000'000; // reward for winning move
            }
        }

        if (!black_window) { // If the window has no Black stones, evaluate White stones
            int bits = __builtin_popcount(white_window);
            if (bits > 1)
            {
                value -= (1 << (3 * (bits - 2)));
                if (bits == 5 && value > -100'000)
                    value -= 1'000'000;
            }
        }
    }
}

static inline void scan_diagonal(const uint32_t* __restrict__ board_turn, const uint32_t* __restrict__ board_not_turn, 
                        int start_row, int start_col, int length,
                        bool is_anti_diagonal, int& value)
{
    uint32_t diagonal_bits = 0;
    uint32_t diagonal_opponent = 0;
    
    for (int i = 0; i < length; i++) {
        int row = start_row + i;
        int col = is_anti_diagonal ? start_col - i : start_col + i;
        diagonal_bits |= ((board_turn[row] >> col) & 1) << i;
        diagonal_opponent |= ((board_not_turn[row] >> col) & 1) << i;
    }
    evaluate_line(diagonal_bits, diagonal_opponent, length, value);
}

int bitwise_heuristic(const uint32_t* __restrict__ board_turn, const uint32_t* __restrict__ board_not_turn, int capture, int capture_opponent)
{
    int value = 0;

    if (capture > 4)
        value += 1000000;
    if (capture_opponent > 4)
        value -= 1000000;

    int top = 0;
    while (top < ROW_SIZE && board_turn[top] == 0 && board_not_turn[top] == 0)
        top++;
    int bottom = ROW_SIZE - 1;
    while (bottom >= 0 && board_turn[bottom] == 0 && board_not_turn[bottom] == 0)
        bottom--;

    int left = 0;
    uint32_t col_bits;
    while (left < ROW_SIZE) {
        col_bits = 0;
        for (int row = 0; row < ROW_SIZE; row++) {
            col_bits |= ((board_turn[row] >> left) & 1);
            col_bits |= ((board_not_turn[row] >> left) & 1);
        }
        if (col_bits != 0) break;
        left++;
    }

    // Find right column
    int right = ROW_SIZE - 1;
    while (right >= 0) {
        col_bits = 0;
        for (int row = 0; row < ROW_SIZE; row++) {
            col_bits |= ((board_turn[row] >> right) & 1);
            col_bits |= ((board_not_turn[row] >> right) & 1);
        }
        if (col_bits != 0) break;
        right--;
    }

    // Calculate expanded bounds
    int expand = WINDOW_SIZE - 1;
    int top_exp = (top - expand < 0) ? 0 : top - expand;
    int bottom_exp = (bottom + expand >= ROW_SIZE) ? ROW_SIZE - 1 : bottom + expand;
    int left_exp = (left - expand < 0) ? 0 : left - expand;
    int right_exp = (right + expand >= ROW_SIZE) ? ROW_SIZE - 1 : right + expand;

    // Horizontal scan
    for (int row = top; row <= bottom; row++) {
        evaluate_line(board_turn[row], board_not_turn[row], ROW_SIZE, value);
    }

     // Vertical scan
    for (int col = left; col <= right; col++) {
        uint32_t vertical_bits = 0;
        uint32_t vertical_opponent = 0;
        for (int row = top_exp; row <= bottom_exp; row++) {
            vertical_bits |= ((board_turn[row] >> col) & 1) << (row - top_exp);
            vertical_opponent |= ((board_not_turn[row] >> col) & 1) << (row - top_exp);
        }
        
        evaluate_line(vertical_bits, vertical_opponent, bottom_exp - top_exp + 1, value);

    }

    // Main diagonal scan (↘)
    int n = bottom - top + 1;
    int m = right - left + 1;

    for (int k = 0; k < n + m - 1; k++) {
        int start_row = (top_exp + n - k - 1 > top_exp) ? top_exp + n - k - 1 : top_exp;
        int start_col = (left_exp - n + k + 1 > left_exp) ? left_exp - n + k + 1 : left_exp;
        int length = std::min(bottom_exp - start_row + 1, right_exp - start_col + 1);

        if (length >= WINDOW_SIZE) {
            scan_diagonal(board_turn, board_not_turn, start_row, start_col, length, false, value);
        }
    }

    // Anti-diagonal scan (↙)
    for (int k = 0; k < n + m - 1; k++) {
        int start_row = (top_exp + n - k - 1 > top_exp) ? top_exp + n - k - 1 : top_exp;
        int start_col = (right_exp + n - k - 1 < right_exp) ? right_exp + n - k - 1 : right_exp;
        int length = std::min(bottom_exp - start_row + 1, start_col - left_exp + 1);

        if (length >= WINDOW_SIZE) {
            scan_diagonal(board_turn, board_not_turn, start_row, start_col, length, true, value);
        }
    }

    return (16 * (pow(2, capture)) + value) - (16 * pow(2, capture_opponent));
}