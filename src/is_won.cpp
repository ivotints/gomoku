#include "gomoku.hpp"

static inline bool has_eatable_piece_in_line(uint32_t* board_turn, uint32_t* board_not_turn,
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

bool is_won(uint32_t* board_turn, uint32_t* board_not_turn, int capture_opponent) {
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