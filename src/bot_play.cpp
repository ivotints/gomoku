#include "gomoku.hpp"




CaptureResult check_capture(uint32_t* board_turn, uint32_t* board_not_turn, 
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


static inline bool is_winning_move(uint32_t* board_turn, uint32_t* board_not_turn,
                        int move, int turn, int capture) {
    int y = move / 19;
    int x = move % 19;
    
    CaptureResult cap = check_capture(board_turn, board_not_turn, y, x);
    if (cap.capture_count + capture > 4)
        return true;

    board_turn[y] |= (1u << x);
    bool is_win = has_winning_line(board_turn);
    board_turn[y] &= ~(1u << x);
    
    return is_win;
}


int bot_play(uint32_t* board_turn, uint32_t* board_not_turn, bool turn, int* captures) {
    int moves[361];
    int move_count = 0;
    generate_legal_moves(board_turn, board_not_turn, captures[turn], moves, &move_count);

    // Check for winning moves first
    for (int i = 0; i < move_count; i++) {
        if (is_winning_move(board_turn, board_not_turn, moves[i], turn, captures[turn])) {
            return moves[i];
        }
    }

    int best_move = moves[0];
    int best_eval = std::numeric_limits<int>::min();
    int alpha = std::numeric_limits<int>::min();
    int beta = std::numeric_limits<int>::max();

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
        CaptureResult cap = check_capture(new_board_turn, new_board_not_turn, y, x);
        new_board_turn[y] |= (1u << x);
        
        if (cap.capture_count > 0) {
            new_captures[turn] += cap.capture_count;
            for (int j = 0; j < cap.position_count; j++) {
                int pos_y = cap.positions[j] / 19;
                int pos_x = cap.positions[j] % 19;
                new_board_not_turn[pos_y] &= ~(1u << pos_x);
            }
        }

        int eval = minimax(new_board_not_turn, new_board_turn, DEPTH, alpha, beta, false, !turn, new_captures);

        if (eval > best_eval) {
            best_eval = eval;
            best_move = moves[i];
        }
        alpha = std::max(alpha, eval);
    }

    return best_move;
}