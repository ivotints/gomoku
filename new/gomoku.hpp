#pragma once

#include <cstdint>
#include <vector>
#include <iostream>
#include <limits>
#include <utility>
#include <algorithm>
#include <cmath>
#include <cstring>
#include <thread>
#include <vector>
#include <mutex>
#include <random>
#include <cstdlib>
#include <ctime>
#include <unordered_map>

#define ROW_SIZE 19
#define WINDOW_SIZE 5
#define WINDOW_MASK 0b11111
#define DEPTH 4
#define BLACK 0
#define WHITE 1

typedef struct move_s 
{
    uint8_t     y;
    uint8_t     x;
    int         eval;
    uint32_t    boards[2][19];
    uint8_t     captures[2];
} move_t;

struct CaptureResult {
        int capture_count;
        int* positions;
        int position_count;
    };

struct BotResult {
    int move;
    int evaluation;
};

extern "C"
{
    BotResult new_bot_play(uint32_t (&boards)[2][19], bool turn, uint8_t (&captures)[2], int depth);
    int check_capture(uint32_t* board_turn, uint32_t* board_not_turn, int y, int x, int *pos);
    bool is_won(uint32_t* board_turn, uint32_t* board_not_turn, int capture_opponent);
    int bitwise_heuristic(const uint32_t* __restrict__ board_turn, 
                     const uint32_t* __restrict__ board_not_turn,
                     int capture, int capture_opponent);
}

void generate_all_legal_moves(uint32_t* board_turn, uint32_t* board_not_turn, int capture, move_t* moves, short* move_count);
int star_heuristic(uint32_t (&boards)[2][19], bool turn, uint8_t (&captures)[2], uint8_t y, uint8_t x, int eval, uint32_t (&new_boards)[2][19], uint8_t (&new_captures)[2]);


