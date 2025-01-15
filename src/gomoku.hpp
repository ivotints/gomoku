#pragma once

#include <cstdint>
#include <vector>
#include <limits>
#include <utility>
#include <algorithm>
#include <cmath>
#include <cstring>
#include <thread>
#include <vector>
#include <mutex>
#include <random>

#define ROW_SIZE 19
#define WINDOW_SIZE 5
#define WINDOW_MASK 0b11111
#define DEPTH 4

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
    BotResult bot_play(uint32_t* board_turn, uint32_t* board_not_turn, bool turn, int* captures);
    CaptureResult check_capture(uint32_t* board_turn, uint32_t* board_not_turn, int y, int x);
    bool is_won(uint32_t* board_turn, uint32_t* board_not_turn, int capture_opponent);
    int bitwise_heuristic(uint32_t* board_turn, uint32_t* board_not_turn, int capture, int capture_opponent);
}

void generate_legal_moves(uint32_t* board_turn, uint32_t* board_not_turn, int capture, int* moves, int* move_count);
bool has_winning_line(uint32_t* board);
int minimax(uint32_t* board_turn, uint32_t* board_not_turn, int depth, int alpha, int beta, bool maximizing_player, bool turn, int* captures);
