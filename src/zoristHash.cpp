#include <iostream>
#include <vector>
#include <random>
#include <cstdint>
#include <cstring>
#include "gomoku.hpp"

#define TTABLE_SIZE (1 << 20) // 1,048,576 entries

// A basic fixed-size transposition table entry
struct TTEntry {
    uint32_t key;        // Partial key (upper 32 bits of a 64-bit hash)
    int heuristic;
};

static TTEntry ttable[TTABLE_SIZE];

// Zobrist table as before
uint64_t zobristTable[19][19][2];

// Initialize Zobrist table
void initializeZobristTable() {
    static bool initialized = false;
    if (!initialized) {
        std::mt19937_64 rng(std::random_device{}());
        std::uniform_int_distribution<uint64_t> dist(0, UINT64_MAX);

        for (int row = 0; row < 19; ++row) {
            for (int col = 0; col < 19; ++col) {
                for (int player = 0; player < 2; ++player) {
                    zobristTable[row][col][player] = dist(rng);
                }
            }
        }
        
        // Optional: Clear the transposition table
        std::memset(ttable, 0, sizeof(ttable));

        initialized = true;
    }
}

// Compute full 64-bit Zobrist hash
uint64_t computeZobristHash(uint32_t* player1Board, uint32_t* player2Board) {
    uint64_t hash = 0;

    for (int row = 0; row < 19; ++row) {
        uint32_t bitRow = player1Board[row];
        while (bitRow) {
            int bit = __builtin_ctz(bitRow);
            hash ^= zobristTable[row][bit][0];
            bitRow &= ~(1u << bit);
        }
    }

    for (int row = 0; row < 19; ++row) {
        uint32_t bitRow = player2Board[row];
        while (bitRow) {
            int bit = __builtin_ctz(bitRow);
            hash ^= zobristTable[row][bit][1];
            bitRow &= ~(1u << bit);
        }
    }

    return hash;
}

// Update a hash for a single move
uint64_t updateZobristHash(uint64_t currentHash, int row, int col, int player) {
    return currentHash ^ zobristTable[row][col][player];
}

// Retrieve a heuristic from the fixed-size transposition table, if any
bool getHeuristicFromTransposeTable(uint64_t hash, int& heuristicValue) {
    // Use a simple modulo index
    const uint64_t index = hash % TTABLE_SIZE;
    // Extract partial key (upper 32 bits)
    const uint32_t partialKey = static_cast<uint32_t>(hash >> 32);

    if (ttable[index].key == partialKey) {
        heuristicValue = ttable[index].heuristic;
        return true;
    }
    return false;
}

// Store a heuristic value in the transposition table
int storeHeuristicInTransposeTable(uint64_t hash, int heuristicValue) {
    const uint64_t index = hash % TTABLE_SIZE;
    const uint32_t partialKey = static_cast<uint32_t>(hash >> 32);

    // Always replace strategy
    ttable[index].key = partialKey;
    ttable[index].heuristic = heuristicValue;
    return heuristicValue;
}