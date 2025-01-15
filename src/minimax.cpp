#include "gomoku.hpp"

int minimax(uint32_t* board_turn, uint32_t* board_not_turn, int depth, int alpha, int beta, bool maximizing_player, bool turn,int* captures) {
    if (depth == 1) {
        return bitwise_heuristic(board_turn, board_not_turn, captures[turn], captures[not turn]) * (maximizing_player ? 1 : -1);
    }

    int moves[361];  // 19x19 max possible moves
    int move_count = 0;
    generate_legal_moves(board_turn, board_not_turn, captures[turn], moves, &move_count);

    if (maximizing_player) {
        int max_eval = -1000000;
        for (int i = 0; i < move_count; i++) {
            uint32_t new_board_turn[ROW_SIZE];
            uint32_t new_board_not_turn[ROW_SIZE];
            int new_captures[2] = {captures[0], captures[1]};
            
            memcpy(new_board_turn, board_turn, ROW_SIZE * sizeof(uint32_t));
            memcpy(new_board_not_turn, board_not_turn, ROW_SIZE * sizeof(uint32_t));

            int y = moves[i] / 19;
            int x = moves[i] % 19;
            CaptureResult capture = check_capture(new_board_turn, new_board_not_turn, y, x);
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
                is_won(new_board_turn, new_board_not_turn, new_captures[!turn])) {
                return 1000000;
            }

            int eval = minimax(new_board_not_turn, new_board_turn,
                             depth - 1, alpha, beta, false, !turn, new_captures);
            max_eval = std::max(max_eval, eval);
            alpha = std::max(alpha, eval);
            if (beta <= alpha)
                break;
        }
        return max_eval;
    } else {
        int min_eval = 1000000;
        for (int i = 0; i < move_count; i++) {
            uint32_t new_board_turn[ROW_SIZE];
            uint32_t new_board_not_turn[ROW_SIZE];
            int new_captures[2] = {captures[0], captures[1]};
            
            memcpy(new_board_turn, board_turn, ROW_SIZE * sizeof(uint32_t));
            memcpy(new_board_not_turn, board_not_turn, ROW_SIZE * sizeof(uint32_t));

            int y = moves[i] / 19;
            int x = moves[i] % 19;
            CaptureResult capture = check_capture(new_board_turn, new_board_not_turn, y, x);
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
                is_won(new_board_turn, new_board_not_turn, new_captures[!turn])) {
                return -1000000;
            }

            int eval = minimax(new_board_not_turn, new_board_turn,
                             depth - 1, alpha, beta, true, !turn, new_captures);
            min_eval = std::min(min_eval, eval);
            beta = std::min(beta, eval);
            if (beta <= alpha)
                break;
        }
        return min_eval;
    }
}