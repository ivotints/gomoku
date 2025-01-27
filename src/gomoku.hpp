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
#include <shared_mutex>

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
    uint8_t     capture_dir;
    u_int64_t  hash;
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
void initializeZobristTable();
uint64_t computeZobristHash(uint32_t* player1Board, uint32_t* player2Board, int depth);
uint64_t updateZobristHash(uint64_t currentHash, uint8_t row, uint8_t col, int player, int depth);
bool isPositionVisited(uint64_t* table, uint64_t hash);
int star_heuristic(uint32_t (&boards)[2][19], bool turn, uint8_t (&captures)[2], uint8_t y, uint8_t x, int eval, uint32_t (&new_boards)[2][19], uint8_t (&new_captures)[2], uint8_t &capture_dir);
bool is_legal_lite(int capture, uint32_t* board_turn, uint32_t* board_not_turn, int y, int x);

void initial_move_generation(uint32_t (&boards)[2][19], move_t* moves, short* move_count);
void sort_moves(move_t (&moves)[300], short move_count, bool turn);
bool find_move(move_t* moves, uint8_t x, uint8_t y, short move_count);