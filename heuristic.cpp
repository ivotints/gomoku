#include <cmath>
#include <algorithm>
#include <limits>
#include <cstring>
#include <vector>
#include "heuristic.h"
# define DEPTH 4

bool is_winning_move_cpp(uint32_t* board_turn, uint32_t* board_not_turn,
                        int move, int turn, int capture) {
    int y = move / 19;
    int x = move % 19;
    
    CaptureResult cap = check_capture_cpp(board_turn, board_not_turn, y, x);
    if (cap.capture_count + capture > 4)
        return true;

    board_turn[y] |= (1u << x);
    bool is_win = has_winning_line(board_turn);
    board_turn[y] &= ~(1u << x);
    
    return is_win;
}

int bot_play_cpp(uint32_t* board_turn, uint32_t* board_not_turn,
                 int turn, int* captures) {
    int moves[361];
    int move_count = 0;
    generate_legal_moves(board_turn, board_not_turn, captures[turn], moves, &move_count);

    // Check for winning moves first
    for (int i = 0; i < move_count; i++) {
        if (is_winning_move_cpp(board_turn, board_not_turn, moves[i], turn, captures[turn])) {
            return moves[i];
        }
    }

    int best_move = moves[0];
    int best_eval = MIN_INT;
    int alpha = MIN_INT;
    int beta = MAX_INT;

    // Try each move
    for (int i = 0; i < move_count; i++) {
        uint32_t new_board_turn[ROW_SIZE];
        uint32_t new_board_not_turn[ROW_SIZE];
        int new_captures[2] = {captures[0], captures[1]};

        memcpy(new_board_turn, board_turn, ROW_SIZE * sizeof(uint32_t));
        memcpy(new_board_not_turn, board_not_turn, ROW_SIZE * sizeof(uint32_t));

        // Apply move
        int y = moves[i] / 19;
        int x = moves[i] % 19;
        CaptureResult cap = check_capture_cpp(new_board_turn, new_board_not_turn, y, x);
        new_board_turn[y] |= (1u << x);
        
        if (cap.capture_count > 0) {
            new_captures[turn] += cap.capture_count;
            for (int j = 0; j < cap.position_count; j++) {
                int pos_y = cap.positions[j] / 19;
                int pos_x = cap.positions[j] % 19;
                new_board_not_turn[pos_y] &= ~(1u << pos_x);
            }
        }

        int eval = minimax_cpp(new_board_not_turn, new_board_turn,
                             DEPTH, alpha, beta, false, !turn, new_captures);

        if (eval > best_eval) {
            best_eval = eval;
            best_move = moves[i];
        }
        alpha = std::max(alpha, eval);
    }

    return best_move;
}

int minimax_cpp(uint32_t* board_turn, uint32_t* board_not_turn,
                int depth, int alpha, int beta,
                bool maximizing_player, int turn,
                int* captures) {
    if (depth == 1) {
        return bitwise_heuristic(board_turn, board_not_turn, 
                               captures[turn], captures[not turn]);
    }

    int moves[361];  // 19x19 max possible moves
    int move_count = 0;
    generate_legal_moves(board_turn, board_not_turn, captures[turn], moves, &move_count);

    if (maximizing_player) {
        int max_eval = MIN_INT;
        for (int i = 0; i < move_count; i++) {
            // Create copies of boards and captures
            uint32_t new_board_turn[ROW_SIZE];
            uint32_t new_board_not_turn[ROW_SIZE];
            int new_captures[2] = {captures[0], captures[1]};
            
            memcpy(new_board_turn, board_turn, ROW_SIZE * sizeof(uint32_t));
            memcpy(new_board_not_turn, board_not_turn, ROW_SIZE * sizeof(uint32_t));

            // Apply move
            int y = moves[i] / 19;
            int x = moves[i] % 19;
            CaptureResult capture = check_capture_cpp(new_board_turn, new_board_not_turn, y, x);
            new_board_turn[y] |= (1u << x);
            
            if (capture.capture_count > 0) {
                new_captures[turn] += capture.capture_count;
                for (int j = 0; j < capture.position_count; j++) {
                    int pos_y = capture.positions[j] / 19;
                    int pos_x = capture.positions[j] % 19;
                    new_board_not_turn[pos_y] &= ~(1u << pos_x);
                }
            }

            if (new_captures[turn] > 4 || 
                is_won_cpp(new_board_turn, new_board_not_turn, turn, new_captures[!turn])) {
                return MAX_INT;
            }

            int eval = minimax_cpp(new_board_not_turn, new_board_turn,
                                 depth - 1, alpha, beta, false, !turn, new_captures);
            max_eval = std::max(max_eval, eval);
            alpha = std::max(alpha, eval);
            if (beta <= alpha)
                break;
        }
        return max_eval;
    } else {
        int min_eval = MAX_INT;
        for (int i = 0; i < move_count; i++) {
            uint32_t new_board_turn[ROW_SIZE];
            uint32_t new_board_not_turn[ROW_SIZE];
            int new_captures[2] = {captures[0], captures[1]};
            
            memcpy(new_board_turn, board_turn, ROW_SIZE * sizeof(uint32_t));
            memcpy(new_board_not_turn, board_not_turn, ROW_SIZE * sizeof(uint32_t));

            int y = moves[i] / 19;
            int x = moves[i] % 19;
            CaptureResult capture = check_capture_cpp(new_board_turn, new_board_not_turn, y, x);
            new_board_turn[y] |= (1u << x);
            
            if (capture.capture_count > 0) {
                new_captures[turn] += capture.capture_count;
                for (int j = 0; j < capture.position_count; j++) {
                    int pos_y = capture.positions[j] / 19;
                    int pos_x = capture.positions[j] % 19;
                    new_board_not_turn[pos_y] &= ~(1u << pos_x);
                }
            }

            if (new_captures[turn] > 4 || 
                is_won_cpp(new_board_turn, new_board_not_turn, turn, new_captures[!turn])) {
                return MIN_INT;
            }

            int eval = minimax_cpp(new_board_not_turn, new_board_turn,
                                 depth - 1, alpha, beta, true, !turn, new_captures);
            min_eval = std::min(min_eval, eval);
            beta = std::min(beta, eval);
            if (beta <= alpha)
                break;
        }
        return min_eval;
    }
}



bool has_eatable_piece_in_line(uint32_t* board_turn, uint32_t* board_not_turn,
                              int y, int x, const int directions[8][2]) {
    const int BOARD_SIZE = 19;

    for (int d = 0; d < 8; d++) {
        int dy = directions[d][0];
        int dx = directions[d][1];
        
        // Check bounds for all positions
        int y2 = y + dy*2;
        int y_prev = y - dy;
        int x2 = x + dx*2;
        int x_prev = x - dx;
        
        if (x2 < 0 || x2 >= BOARD_SIZE || y2 < 0 || y2 >= BOARD_SIZE ||
            x_prev < 0 || x_prev >= BOARD_SIZE || y_prev < 0 || y_prev >= BOARD_SIZE) {
            continue;
        }
        
        // First pattern: opponent piece surrounded by two player pieces
        if (((board_turn[y + dy] >> (x + dx)) & 1) && 
            ((board_not_turn[y_prev] >> x_prev) & 1) && 
            !((board_not_turn[y2] >> x2) & 1) &&
            !((board_turn[y2] >> x2) & 1)) {
            return true;
        }
        
        // Second pattern: opponent piece with space on one side
        if (((board_turn[y + dy] >> (x + dx)) & 1) && 
            ((board_not_turn[y2] >> x2) & 1) && 
            !((board_not_turn[y_prev] >> x_prev) & 1) &&
            !((board_turn[y_prev] >> x_prev) & 1)) {
            return true;
        }
    }
    return false;
}

bool is_won_cpp(uint32_t* board_turn, uint32_t* board_not_turn, int turn, int capture_opponent) {
    const int BOARD_SIZE = 19;
    const int directions[4][2] = {{0,1}, {1,1}, {1,0}, {1,-1}};
    const int capture_directions[8][2] = {
        {0,1}, {1,1}, {1,0}, {1,-1}, {0,-1}, {-1,-1}, {-1,0}, {-1,1}
    };
    
    for (int i = 0; i < BOARD_SIZE - 4; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (!(board_turn[i] & (1u << j))) {
                continue;
            }
            
            for (const auto& dir : directions) {
                int end_y = i + 4*dir[0];
                int end_x = j + 4*dir[1];
                
                if (end_y >= BOARD_SIZE || end_y < 0 || 
                    end_x >= BOARD_SIZE || end_x < 0) {
                    continue;
                }
                
                bool valid = true;
                for (int k = 1; k < 5; k++) {
                    int next_y = i + k*dir[0];
                    int next_x = j + k*dir[1];
                    if (!(board_turn[next_y] & (1u << next_x))) {
                        valid = false;
                        break;
                    }
                }
                
                if (valid) {
                    // Check if opponent with 4 captures can prevent win
                    if (capture_opponent == 4) {
                        bool can_prevent = false;
                        for (int k = 0; k < 5; k++) {
                            int y = i + k*dir[0];
                            int x = j + k*dir[1];
                            if (has_eatable_piece_in_line(board_turn, board_not_turn, 
                                                        y, x, capture_directions)) {
                                can_prevent = true;
                                break;
                            }
                        }
                        if (can_prevent) {
                            continue;
                        }
                    }
                    return true;
                }
            }
        }
    }
    return false;
}

CaptureResult check_capture_cpp(uint32_t* board_turn, uint32_t* board_not_turn, 
                              int y, int x) {
    const int BOARD_SIZE = 19;
    static std::vector<int> positions;  // Static to avoid reallocations
    positions.clear();
    int capture = 0;
    
    const int directions[8][2] = {
        {0,1}, {1,1}, {1,0}, {1,-1}, 
        {0,-1}, {-1,-1}, {-1,0}, {-1,1}
    };

    for (const auto& dir : directions) {
        int y3 = y + dir[0]*3;
        int x3 = x + dir[1]*3;
        
        if (x3 < 0 || x3 >= BOARD_SIZE || y3 < 0 || y3 >= BOARD_SIZE)
            continue;

        int bit1 = (y + dir[0]) * BOARD_SIZE + (x + dir[1]);
        int bit2 = (y + dir[0]*2) * BOARD_SIZE + (x + dir[1]*2);

        if (((board_turn[y3] >> x3) & 1) && 
            ((board_not_turn[y + dir[0]*2] >> (x + dir[1]*2)) & 1) && 
            ((board_not_turn[y + dir[0]] >> (x + dir[1])) & 1)) {
            capture++;
            positions.push_back(bit1);
            positions.push_back(bit2);
        }
    }

    CaptureResult result;
    result.capture_count = capture;
    result.position_count = positions.size();
    result.positions = positions.data();
    return result;
}


bool is_capture(uint32_t* board_turn, uint32_t* board_not_turn, int y, int x) {
    const int BOARD_SIZE = 19;
    const int directions[8][2] = {
        {0,1}, {1,1}, {1,0}, {1,-1}, {0,-1}, {-1,-1}, {-1,0}, {-1,1}
    };

    for (const auto& dir : directions) {
        int y3 = y + dir[0]*3;
        int x3 = x + dir[1]*3;
        
        if (x3 < 0 || x3 >= BOARD_SIZE || y3 < 0 || y3 >= BOARD_SIZE)
            continue;

        if (((board_turn[y3] >> x3) & 1) && 
            ((board_not_turn[y + dir[0]*2] >> (x + dir[1]*2)) & 1) && 
            ((board_not_turn[y + dir[0]] >> (x + dir[1])) & 1)) {
            return true;
        }
    }
    return false;
}

bool has_winning_line(uint32_t* board) {
    const int BOARD_SIZE = 19;
    const int directions[4][2] = {{0,1}, {1,1}, {1,0}, {1,-1}};
    
    for (int i = 0; i < BOARD_SIZE - 4; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (!(board[i] & (1u << j))) 
                continue;
                
            for (const auto& dir : directions) {
                int end_y = i + 4*dir[0];
                int end_x = j + 4*dir[1];
                
                if (end_y >= BOARD_SIZE || end_y < 0 || 
                    end_x >= BOARD_SIZE || end_x < 0)
                    continue;
                
                bool valid = true;
                for (int k = 1; k < 5; k++) {
                    int next_y = i + k*dir[0];
                    int next_x = j + k*dir[1];
                    if (!(board[next_y] & (1u << next_x))) {
                        valid = false;
                        break;
                    }
                }
                if (valid)
                    return true;
            }
        }
    }
    return false;
}

inline bool check_pattern(uint32_t self_bits, uint32_t opp_bits, int space, int pattern_len, 
                        const uint32_t* PATTERNS, const uint32_t* MASKS) {
    uint32_t pattern = pattern_len == 5 ? PATTERNS[0] : PATTERNS[1];
    uint32_t pattern2 = pattern_len == 6 ? PATTERNS[2] : 0;
    uint32_t mask = MASKS[pattern_len - 5];
    
    for (int shift = 0; shift <= space - pattern_len; shift++) {
        if ((opp_bits >> shift) & mask) continue;
        uint32_t chunk = (self_bits >> shift) & mask;
        if (chunk == pattern || chunk == pattern2) return true;
    }
    return false;
}

inline std::pair<int, int> compute_spaces(int coord, int pattern_len, int BOARD_SIZE) {
    int max_extra = pattern_len - 2;
    int left = std::min(coord, max_extra);
    int right = std::min(BOARD_SIZE - 1 - coord, max_extra);
    return {left, left + right + 1};
}
bool check_double_three(uint32_t* board_turn, uint32_t* board_not_turn, int y, int x) {
    
    const int BOARD_SIZE = 19;
    const uint32_t PATTERNS[3] = {0b01110, 0b010110, 0b011010};
    const uint32_t MASKS[2] = {0b11111, 0b111111};
    const int PATTERN_LENGTHS[2] = {5, 6};

    board_turn[y] |= (1u << x);
    int count = 0;

    for (int pattern_len : PATTERN_LENGTHS) {
        // Horizontal check
        auto [left, bits_space] = compute_spaces(x, pattern_len, BOARD_SIZE);
        if (bits_space >= pattern_len) {
            uint32_t row_self = (board_turn[y] >> (x - left)) & ((1 << bits_space) - 1);
            uint32_t row_opp = (board_not_turn[y] >> (x - left)) & ((1 << bits_space) - 1);
            if (check_pattern(row_self, row_opp, bits_space, pattern_len, PATTERNS, MASKS)) count++;
        }

        // Vertical check
        auto [top, v_bits_space] = compute_spaces(y, pattern_len, BOARD_SIZE);
        if (v_bits_space >= pattern_len) {
            uint32_t col_self = 0, col_opp = 0;
            for (int i = 0; i < v_bits_space; i++) {
                col_self |= ((board_turn[y - top + i] >> x) & 1) << i;
                col_opp |= ((board_not_turn[y - top + i] >> x) & 1) << i;
            }
            if (check_pattern(col_self, col_opp, v_bits_space, pattern_len, PATTERNS, MASKS)) count++;
        }

        // Diagonal (\) check
        auto [d_left, d_bits_space] = compute_spaces(std::min(y, x), pattern_len, BOARD_SIZE);
        if (d_bits_space >= pattern_len) {
            uint32_t diag_self = 0, diag_opp = 0;
            for (int i = 0; i < d_bits_space; i++) {
                diag_self |= ((board_turn[y - d_left + i] >> (x - d_left + i)) & 1) << i;
                diag_opp |= ((board_not_turn[y - d_left + i] >> (x - d_left + i)) & 1) << i;
            }
            if (check_pattern(diag_self, diag_opp, d_bits_space, pattern_len, PATTERNS, MASKS)) count++;
        }

        // Anti-diagonal (/) check
        int d_down = std::min({BOARD_SIZE - 1 - y, x, pattern_len - 2});
        int d_up = std::min({y, BOARD_SIZE - 1 - x, pattern_len - 2});
        int ad_bits_space = d_down + d_up + 1;
        if (ad_bits_space >= pattern_len) {
            uint32_t adiag_self = 0, adiag_opp = 0;
            for (int i = 0; i < ad_bits_space; i++) {
                adiag_self |= ((board_turn[y + d_down - i] >> (x - d_down + i)) & 1) << i;
                adiag_opp |= ((board_not_turn[y + d_down - i] >> (x - d_down + i)) & 1) << i;
            }
            if (check_pattern(adiag_self, adiag_opp, ad_bits_space, pattern_len, PATTERNS, MASKS)) count++;
        }
    }

    board_turn[y] &= ~(1u << x);
    return count > 1;
}

bool is_legal_lite(int capture, uint32_t* board_turn, uint32_t* board_not_turn, int y, int x) {
    if (!is_capture(board_turn, board_not_turn, y, x) && ((capture == 4 && has_winning_line(board_not_turn)) || check_double_three(board_turn, board_not_turn, y, x))) {
        return false;
    }
    return true;
}




void generate_legal_moves(uint32_t* board_turn, uint32_t* board_not_turn,
                          int capture, int* moves, int* move_count) {
    *move_count = 0;

    // Create union board
    uint32_t union_board[ROW_SIZE];
    for(int i = 0; i < ROW_SIZE; i++) {
        union_board[i] = board_turn[i] | board_not_turn[i];
    }

    // Find bounding box
    int top = 0;
    while (top < ROW_SIZE && union_board[top] == 0) top++;
    
    int bottom = ROW_SIZE - 1;
    while (bottom >= 0 && union_board[bottom] == 0) bottom--;

    int left = 0;
    uint32_t col_bits;
    while (left < ROW_SIZE) {
        col_bits = 0;
        for (int row = 0; row < ROW_SIZE; row++) {
            col_bits |= ((union_board[row] >> left) & 1);
        }
        if (col_bits != 0) break;
        left++;
    }

    int right = ROW_SIZE - 1;
    while (right >= 0) {
        col_bits = 0;
        for (int row = 0; row < ROW_SIZE; row++) {
            col_bits |= ((union_board[row] >> right) & 1);
        }
        if (col_bits != 0) break;
        right--;
    }

    // Expand bounding box
    int expand = 1;
    top = (top - expand < 0) ? 0 : top - expand;
    bottom = (bottom + expand >= ROW_SIZE) ? ROW_SIZE - 1 : bottom + expand;
    left = (left - expand < 0) ? 0 : left - expand;
    right = (right + expand >= ROW_SIZE) ? ROW_SIZE - 1 : right + expand;

    // Iterate through bounding box
    uint32_t mask = (right - left == 1) ? 0b11 : 0b111;
    
    for (int row = top; row <= bottom; row++) {
        for (int col = left; col <= right; col++) {
            uint32_t window_mask = 0;
            
            for (int i = -1; i <= 1; i++) {
                int check_row = row + i;
                if (check_row < top || check_row > bottom) continue;
                
                int check_col = (col - 1 > left) ? col - 1 : left;
                int shift_pos = check_col;
                window_mask |= (union_board[check_row] >> shift_pos) & mask;
            }

            if (window_mask != 0) {
                int bit_pos = row * ROW_SIZE + col;
                if (!(union_board[row] & (1u << col))) {
                    if (is_legal_lite(capture, board_turn, board_not_turn, row, col)) {
                        moves[*move_count] = bit_pos;
                        (*move_count)++;
                    }
                }
            }
        }
    }
}

inline int scan_window(uint32_t window_turn, uint32_t window_opponent, int& value) {
    if (window_opponent == 0) {
        int bits_count = __builtin_popcount(window_turn);
        if (bits_count > 1) {
            if (bits_count == 5) return std::numeric_limits<int>::max();
            value += 1 << (3 * (bits_count - 2));
        }
    }
    
    if (window_turn == 0) {
        int bits_count = __builtin_popcount(window_opponent);
        if (bits_count > 1) {
            if (bits_count == 5) return std::numeric_limits<int>::min();
            value -= 1 << (3 * (bits_count - 2));
        }
    }
    return 0;
}

inline int scan_line(uint32_t bits_line, uint32_t opponent_line, int max_shift, int& value) {
    for (int window_shift = 0; window_shift <= max_shift; window_shift++) {
        uint32_t window_turn = (bits_line >> window_shift) & WINDOW_MASK;
        uint32_t window_opponent = (opponent_line >> window_shift) & WINDOW_MASK;
        
        int result = scan_window(window_turn, window_opponent, value);
        if (result != 0) return result;
    }
    return 0;
}

inline int scan_diagonal(uint32_t* board_turn, uint32_t* board_not_turn, 
                        int start_row, int start_col, int length,
                        bool is_anti_diagonal, int& value) {
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

int bitwise_heuristic(uint32_t* board_turn, uint32_t* board_not_turn, int capture, int capture_opponent) {
    int value = 0;

    if (capture > 4)
        return std::numeric_limits<int>::max();
    if (capture_opponent > 4)
        return std::numeric_limits<int>::min();

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