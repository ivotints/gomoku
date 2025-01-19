#include <iostream>
#include <vector>
#include <random>
#include <cstdint>
#include "gomoku.hpp"

uint64_t zobristTable[19][19][2];
std::unordered_map<uint64_t, int> transposeTable;

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
        initialized = true;
    }
}

uint64_t computeZobristHash(uint32_t* player1Board, uint32_t* player2Board) {
    uint64_t hash = 0;

    for (int row = 0; row < 19; ++row) {
        uint32_t bitRow = player1Board[row];
        for (int bit = 0; bit < 19; ++bit) {
            if (bitRow & (1u << bit)) {
                hash ^= zobristTable[row][bit][0];
            }
        }
    }

    for (int row = 0; row < 19; ++row) {
        uint32_t bitRow = player2Board[row];
        for (int bit = 0; bit < 19; ++bit) {
            if (bitRow & (1u << bit)) {
                hash ^= zobristTable[row][bit][1];
            }
        }
    }

    return hash;
}

uint64_t updateZobristHash(uint64_t currentHash, int row, int col, int player) {
    return currentHash ^ zobristTable[row][col][player];
}

bool getHeuristicFromTransposeTable(uint64_t hash, int& heuristicValue) {
    auto it = transposeTable.find(hash);
    if (it != transposeTable.end()) {
        heuristicValue = it->second;
        return true;
    }
    return false;
}

int storeHeuristicInTransposeTable(uint64_t hash, int heuristicValue) {
    transposeTable[hash] = heuristicValue;
    return heuristicValue;
}