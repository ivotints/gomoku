#ifndef HEURISTIC_H
#define HEURISTIC_H

#include <cstdint>

#define ROW_SIZE 19
#define WINDOW_SIZE 5
#define WINDOW_MASK 0b11111

extern "C" {
    int bitwise_heuristic(uint32_t* board_turn, uint32_t* board_not_turn, 
                         int capture, int capture_opponent);
    void generate_legal_moves(uint32_t* board_turn, uint32_t* board_not_turn,
                            int capture,
                            int* moves, int* move_count);
    bool is_legal_lite(int capture, uint32_t* board_turn, uint32_t* board_not_turn, 
                    int y, int x);
}


#endif