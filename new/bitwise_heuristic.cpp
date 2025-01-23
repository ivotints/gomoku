#include "gomoku.hpp"

static inline int scan_window(uint32_t window_turn, uint32_t window_opponent, int& value)
{
    if (window_opponent == 0) {
        int bits_count = __builtin_popcount(window_turn);
        if (bits_count > 1) {
            if (bits_count == 5) return 1'000'000;
            value += 1 << (3 * (bits_count - 2));
        }
    }
    
    if (window_turn == 0) {
        int bits_count = __builtin_popcount(window_opponent);
        if (bits_count > 1) {
            if (bits_count == 5) return -1'000'000;
            value -= 1 << (3 * (bits_count - 2));
        }
    }
    return 0;
}

static inline int scan_line(uint32_t bits_line, uint32_t opponent_line, int max_shift, int& value)
{
    for (int window_shift = 0; window_shift <= max_shift; window_shift++) {
        uint32_t window_turn = (bits_line >> window_shift) & WINDOW_MASK;
        uint32_t window_opponent = (opponent_line >> window_shift) & WINDOW_MASK;
        
        int result = scan_window(window_turn, window_opponent, value);
        if (result != 0) return result;
    }
    return 0;
}

static inline int scan_diagonal(const uint32_t* __restrict__ board_turn, const uint32_t* __restrict__ board_not_turn, 
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
    
    return scan_line(diagonal_bits, diagonal_opponent, length - WINDOW_SIZE, value);
}

int bitwise_heuristic(const uint32_t* __restrict__ board_turn, const uint32_t* __restrict__ board_not_turn, int capture, int capture_opponent)
{
    int value = 0;

    if (capture > 4)
        return 1000000;
    if (capture_opponent > 4)
        return -1000000;

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
        int result = scan_line(board_turn[row], 
                             board_not_turn[row], 
                             ROW_SIZE - WINDOW_SIZE,
                             value);
        if (result != 0) return result;
    }

     // Vertical scan
    for (int col = left; col <= right; col++) {
        uint32_t vertical_bits = 0;
        uint32_t vertical_opponent = 0;
        for (int row = top_exp; row <= bottom_exp; row++) {
            vertical_bits |= ((board_turn[row] >> col) & 1) << (row - top_exp);
            vertical_opponent |= ((board_not_turn[row] >> col) & 1) << (row - top_exp);
        }
        
        int result = scan_line(vertical_bits,
                             vertical_opponent,
                             bottom_exp - top_exp - WINDOW_SIZE + 1,
                             value);
        if (result != 0) return result;
    }

    // Main diagonal scan (↘)
    int n = bottom - top + 1;
    int m = right - left + 1;

    for (int k = 0; k < n + m - 1; k++) {
        int start_row = (top_exp + n - k - 1 > top_exp) ? top_exp + n - k - 1 : top_exp;
        int start_col = (left_exp - n + k + 1 > left_exp) ? left_exp - n + k + 1 : left_exp;
        int length = std::min(bottom_exp - start_row + 1, right_exp - start_col + 1);

        if (length >= WINDOW_SIZE) {
            int result = scan_diagonal(board_turn, board_not_turn, 
                                     start_row, start_col, length, 
                                     false, value);
            if (result != 0) return result;
        }
    }

    // Anti-diagonal scan (↙)
    for (int k = 0; k < n + m - 1; k++) {
        int start_row = (top_exp + n - k - 1 > top_exp) ? top_exp + n - k - 1 : top_exp;
        int start_col = (right_exp + n - k - 1 < right_exp) ? right_exp + n - k - 1 : right_exp;
        int length = std::min(bottom_exp - start_row + 1, start_col - left_exp + 1);

        if (length >= WINDOW_SIZE) {
            int result = scan_diagonal(board_turn, board_not_turn,
                                     start_row, start_col, length,
                                     true, value);
            if (result != 0) return result;
        }
    }

    return (16 * (pow(2, capture)) + value) - (16 * pow(2, capture_opponent));
}