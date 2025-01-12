#ifndef HEURISTIC_H
#define HEURISTIC_H

#include <cstdint>

extern "C" {
    double bitwise_heuristic(uint32_t* board_turn, uint32_t* board_not_turn, int capture, int capture_opponent);
}

#endif