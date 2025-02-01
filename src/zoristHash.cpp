
#include "gomoku.hpp"

namespace {
    bool initialized = false;
}

static uint64_t zobristTable[19][19][2];
static uint64_t zobristDepth[11];

void initializeZobristTable() {
    if (!initialized) {
        std::mt19937_64 rng(0);
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

bool isPositionVisited(table_t* table, uint64_t hash, int& value) {
    static const uint64_t TABLE_SIZE = 1'000'000;
    uint64_t startIndex = hash % TABLE_SIZE;
    uint64_t i = startIndex;

    while (true) {
        if (table[i].hash == 0) {
            return false;
        }
        if (table[i].hash == hash) {
            value = table[i].value;
            return true;
        }
        i = (i + 1) % TABLE_SIZE;
        if (i == startIndex) {
            std::cout << "Table full, unable to insert: " << hash << std::endl;
            return false;
        }
    }
}