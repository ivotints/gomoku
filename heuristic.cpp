#include "heuristic.h"
#include <cmath>

double bitwise_heuristic(uint32_t* board_turn, uint32_t* board_not_turn, int capture, int capture_opponent) {
    const int ROW_SIZE = 19;
    const int WINDOW_SIZE = 5;
    const uint32_t WINDOW_MASK = 0b11111;
    double value = 0;

    // Early capture checks
    if (capture > 4) return INFINITY;
    if (capture_opponent > 4) return -INFINITY;

    // Find bounding box - top row
    int top = 0;
    while (top < ROW_SIZE && board_turn[top] == 0 && board_not_turn[top] == 0) {
        top++;
    }

    // Find bottom row
    int bottom = ROW_SIZE - 1;
    while (bottom >= 0 && board_turn[bottom] == 0 && board_not_turn[bottom] == 0) {
        bottom--;
    }

    // Find left column
    int left = 0;
    uint32_t col_bits;
    while (left < ROW_SIZE) {
        col_bits = 0;
        for (int row = 0; row < ROW_SIZE; row++) {
            col_bits |= ((board_turn[row] >> left) & 1) << row;
            col_bits |= ((board_not_turn[row] >> left) & 1) << row;
        }
        if (col_bits != 0) break;
        left++;
    }

    // Find right column
    int right = ROW_SIZE - 1;
    while (right >= 0) {
        col_bits = 0;
        for (int row = 0; row < ROW_SIZE; row++) {
            col_bits |= ((board_turn[row] >> right) & 1) << row;
            col_bits |= ((board_not_turn[row] >> right) & 1) << row;
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

    // Horizontal scan - we can do it directly now since each row is single int
    for (int row = top; row <= bottom; row++) {
        uint32_t current_row = board_turn[row];
        uint32_t current_row_opponent = board_not_turn[row];
        
        // Scan windows in this row
        for (int window_shift = 0; window_shift <= ROW_SIZE - WINDOW_SIZE; window_shift++) {
            uint32_t window_turn = (current_row >> window_shift) & WINDOW_MASK;
            uint32_t window_opponent = (current_row_opponent >> window_shift) & WINDOW_MASK;
            
            if (window_opponent == 0) {
                int bits_count = __builtin_popcount(window_turn);
                if (bits_count > 1) {
                    if (bits_count == 5) return INFINITY;
                    value += 1 << (3 * (bits_count - 2));
                }
            }
            
            if (window_turn == 0) {
                int bits_count = __builtin_popcount(window_opponent);
                if (bits_count > 1) {
                    if (bits_count == 5) return -INFINITY;
                    value -= 1 << (3 * (bits_count - 2));
                }
            }
        }
    }

    // Vertical scan
    for (int col = left; col <= right; col++) {
        uint32_t vertical_bits = 0;
        uint32_t vertical_opponent = 0;
        for (int row = top_exp; row <= bottom_exp; row++) {
            vertical_bits |= ((board_turn[row] >> col) & 1) << (row - top_exp);
            vertical_opponent |= ((board_not_turn[row] >> col) & 1) << (row - top_exp);
        }
        
        for (int window_shift = 0; window_shift <= bottom_exp - top_exp - WINDOW_SIZE + 1; window_shift++) {
            uint32_t window_turn = (vertical_bits >> window_shift) & WINDOW_MASK;
            uint32_t window_opponent = (vertical_opponent >> window_shift) & WINDOW_MASK;
            
            if (window_opponent == 0) {
                int bits_count = __builtin_popcount(window_turn);
                if (bits_count > 1) {
                    if (bits_count == 5) return INFINITY;
                    value += 1 << (3 * (bits_count - 2));
                }
            }
            
            if (window_turn == 0) {
                int bits_count = __builtin_popcount(window_opponent);
                if (bits_count > 1) {
                    if (bits_count == 5) return -INFINITY;
                    value -= 1 << (3 * (bits_count - 2));
                }
            }
        }
    }

    // Main diagonal scan (↘)
    int n = bottom - top + 1;
    int m = right - left + 1;
    
    for (int k = 0; k < n + m - 1; k++) {
        int start_row = (top_exp + n - k - 1 > top_exp) ? top_exp + n - k - 1 : top_exp;
        int start_col = (left_exp - n + k + 1 > left_exp) ? left_exp - n + k + 1 : left_exp;
        int length = std::min(bottom_exp - start_row + 1, right_exp - start_col + 1);
    
        if (length >= WINDOW_SIZE) {
            uint32_t diagonal_bits = 0;
            uint32_t diagonal_opponent = 0;
            for (int i = 0; i < length; i++) {
                int row = start_row + i;
                int col = start_col + i;
                diagonal_bits |= ((board_turn[row] >> col) & 1) << i;
                diagonal_opponent |= ((board_not_turn[row] >> col) & 1) << i;
            }
            
            for (int window_shift = 0; window_shift <= length - WINDOW_SIZE; window_shift++) {
                uint32_t window_turn = (diagonal_bits >> window_shift) & WINDOW_MASK;
                uint32_t window_opponent = (diagonal_opponent >> window_shift) & WINDOW_MASK;
                
                if (window_opponent == 0) {
                    int bits_count = __builtin_popcount(window_turn);
                    if (bits_count > 1) {
                        if (bits_count == 5) return INFINITY;
                        value += 1 << (3 * (bits_count - 2));
                    }
                }
                
                if (window_turn == 0) {
                    int bits_count = __builtin_popcount(window_opponent);
                    if (bits_count > 1) {
                        if (bits_count == 5) return -INFINITY;
                        value -= 1 << (3 * (bits_count - 2));
                    }
                }
            }
        }
    }

    // Anti-diagonal scan (↙)
    for (int k = 0; k < n + m - 1; k++) {
        int start_row = (top_exp + n - k - 1 > top_exp) ? top_exp + n - k - 1 : top_exp;
        int start_col = (right_exp + n - k - 1 < right_exp) ? right_exp + n - k - 1 : right_exp;
        int length = std::min(bottom_exp - start_row + 1, start_col - left_exp + 1);
    
        if (length >= WINDOW_SIZE) {
            uint32_t anti_bits = 0;
            uint32_t anti_opponent = 0;
            for (int i = 0; i < length; i++) {
                int row = start_row + i;
                int col = start_col - i;
                anti_bits |= ((board_turn[row] >> col) & 1) << i;
                anti_opponent |= ((board_not_turn[row] >> col) & 1) << i;
            }
            
            for (int window_shift = 0; window_shift <= length - WINDOW_SIZE; window_shift++) {
                uint32_t window_turn = (anti_bits >> window_shift) & WINDOW_MASK;
                uint32_t window_opponent = (anti_opponent >> window_shift) & WINDOW_MASK;
                
                if (window_opponent == 0) {
                    int bits_count = __builtin_popcount(window_turn);
                    if (bits_count > 1) {
                        if (bits_count == 5) return INFINITY;
                        value += 1 << (3 * (bits_count - 2));
                    }
                }
                
                if (window_turn == 0) {
                    int bits_count = __builtin_popcount(window_opponent);
                    if (bits_count > 1) {
                        if (bits_count == 5) return -INFINITY;
                        value -= 1 << (3 * (bits_count - 2));
                    }
                }
            }
        }
    }

    return (16 * (pow(2, capture)) + value) - (16 * pow(2, capture_opponent));
}