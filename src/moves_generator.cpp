#include "gomoku.hpp"

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

static inline bool check_pattern(uint32_t self_bits, uint32_t opp_bits, int space, int pattern_len, 
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

static inline std::pair<int, int> compute_spaces(int coord, int pattern_len, int BOARD_SIZE) {
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
    if (x < 0 || x >= 19 || y < 0 || y >= 19 || (board_turn[y] & (1U << x)) || (board_not_turn[y] & (1U << x))) return false;
    if (!is_capture(board_turn, board_not_turn, y, x) && ((capture == 4 && has_winning_line(board_not_turn)) || check_double_three(board_turn, board_not_turn, y, x))) {
        return false;
    }
    return true;
}

int light_eval(u_int32_t* board_turn, u_int32_t* board_not_turn, int y, int x) {
    
    return 0;
}

void sort_move(short* moves, int move_count, uint32_t* board_turn, uint32_t* board_not_turn) {
    int value[move_count];
    for (int i = 0; i < move_count; i++) {
        int y = moves[i] / 19;
        int x = moves[i] % 19;
        value[i] = 0;//bitwise_heuristic(board_turn, board_not_turn, 0, 0);
    }
    std::vector<int> order(move_count);
    for (int i = 0; i < move_count; ++i) {
        order[i] = i;
    }

    std::sort(order.begin(), order.end(), [&](int a, int b) {
        return value[a] > value[b];
    });

    std::vector<bool> visited(move_count, false);
    for (int i = 0; i < move_count; ++i) {
        if (visited[i] || order[i] == i) {
            continue;
        }

        int current = i;
        while (!visited[current]) {
            visited[current] = true;
            int next = order[current];
            std::swap(moves[current], moves[next]);
            current = next;
        }
    }
}

void find_and_remove(short move, short* moves, int* move_count) {
    for (int i = 0; i < *move_count; i++) {
        if (moves[i] == move) {
            memmove(&moves[i], &moves[i + 1], (*move_count - i - 1) * sizeof(short));
            (*move_count)--;
            return;
        }
    }
    return;
}

bool find_move(short* moves, short move, int count) {
    for (int i = 0; i < count; i++) {
        if (moves[i] == move) return true;
    }
    return false;
}
void generate_legal_moves(uint32_t* board_turn, uint32_t* board_not_turn, int capture, short* moves, int* move_count, short last_move) {
    int x = last_move % 19;
    int y = last_move / 19;
    find_and_remove(last_move, moves, move_count);
    if (!find_move(moves, last_move + 19, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y+1, x))       moves[(*move_count)++] = (y+1) * 19 + x;
    if (!find_move(moves, last_move + 20, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y+1, x+1))     moves[(*move_count)++] = (y+1) * 19 + (x+1);
    if (!find_move(moves, last_move + 18, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y+1, x-1))     moves[(*move_count)++] = (y+1) * 19 + (x-1);
    if (!find_move(moves, last_move - 18, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y-1, x+1))     moves[(*move_count)++] = (y-1) * 19 + (x+1);
    if (!find_move(moves, last_move - 20, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y-1, x-1))     moves[(*move_count)++] = (y-1) * 19 + (x-1);
    if (!find_move(moves, last_move - 19, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y-1, x))       moves[(*move_count)++] = (y-1) * 19 + x;
    if (!find_move(moves, last_move - 1, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y, x-1))        moves[(*move_count)++] = y * 19 + (x-1);
    if (!find_move(moves, last_move + 1, *move_count) && is_legal_lite(capture, board_turn, board_not_turn, y, x+1))        moves[(*move_count)++] = y * 19 + (x+1);
    sort_move(moves, *move_count, board_turn, board_not_turn);
}