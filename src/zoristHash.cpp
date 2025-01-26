
#include "gomoku.hpp"

namespace {
    bool initialized = false;
}

uint64_t zobristTable[19][19][2] = {{{0}}};
uint64_t zobristDepth[11] = {0};
void initializeZobristTable() {
    if (!initialized) {
        std::mt19937_64 rng(std::random_device{}());
        std::uniform_int_distribution<uint64_t> dist(0, UINT64_MAX);

        for (int d = 0; d < 11; ++d) {
            zobristDepth[d] = dist(rng);
        }

        for (int row = 0; row < 19; ++row) {
            for (int col = 0; col < 19; ++col) {
                for (int player = 0; player < 2; ++player) {
                    zobristTable[row][col][player] = dist(rng);
                }
            }
        }
        initialized = true;
    }
}

uint64_t computeZobristHash(uint32_t* player1Board, uint32_t* player2Board, int depth) {
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

    hash ^= zobristDepth[depth];
    return hash;
}

uint64_t updateZobristHash(uint64_t currentHash, uint8_t row, uint8_t col, int player, int depth) {
    currentHash ^= zobristDepth[depth + 1];
    currentHash ^= zobristTable[row][col][player];
    currentHash ^= zobristDepth[depth];
    return currentHash;
}

bool isPositionVisited(uint32_t* table, uint64_t hash) {
    const uint64_t index = hash % 1000000;
    const uint32_t partialKey = static_cast<uint32_t>(hash >> 32);
    if (table[index] == partialKey) {
        return true;
    }
    table[index] = partialKey;
    return false;
}
