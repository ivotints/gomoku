#ifndef HEURISTIC_H
#define HEURISTIC_H

#include <cstdint>
#include <utility>
#include <vector>
#include <limits>

#define ROW_SIZE 19
#define WINDOW_SIZE 5
#define WINDOW_MASK 0b11111

const int MAX_INT = std::numeric_limits<int>::max();
const int MIN_INT = std::numeric_limits<int>::min();

extern "C" {
    int bitwise_heuristic(uint32_t* board_turn, uint32_t* board_not_turn, 
                         int capture, int capture_opponent);
    void generate_legal_moves(uint32_t* board_turn, uint32_t* board_not_turn,
                            int capture,
                            int* moves, int* move_count);
    bool is_legal_lite(int capture, uint32_t* board_turn, uint32_t* board_not_turn, 
                    int y, int x);

    struct CaptureResult {
        int capture_count;
        int* positions;
        int position_count;
    };

    CaptureResult check_capture_cpp(uint32_t* board_turn, uint32_t* board_not_turn, 
                                  int y, int x);
    bool is_won_cpp(uint32_t* board_turn, uint32_t* board_not_turn, 
                    int turn, int capture_opponent);

    int minimax_cpp(uint32_t* board_turn, uint32_t* board_not_turn,
               int depth, int alpha, int beta,
               bool maximizing_player, int turn,
               int* captures);
    int bot_play_cpp(uint32_t* board_turn, uint32_t* board_not_turn,
                    int turn, int* captures);
    

}
    struct PlayResult {
        int move;
        int eval;
    };
    bool has_winning_line(uint32_t* board);


#endif