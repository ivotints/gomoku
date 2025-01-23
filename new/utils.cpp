#include "gomoku.hpp"

int check_capture(uint32_t* board_turn, uint32_t* board_not_turn, 
                              int y, int x, int* pos) {
    const int BOARD_SIZE = 19;
    int capture = 0;
    
    const int directions[8][2] = {
        {0,1}, {1,1}, {1,0}, {1,-1}, 
        {0,-1}, {-1,-1}, {-1,0}, {-1,1}
    };

    for (const auto& dir : directions) {
        int y3 = y + dir[0]*3;
        int x3 = x + dir[1]*3;
        
        if (x3 < 0 || x3 >= BOARD_SIZE || y3 < 0 || y3 >= BOARD_SIZE)
            continue;

        int bit1 = (y + dir[0]) * BOARD_SIZE + (x + dir[1]);
        int bit2 = (y + dir[0]*2) * BOARD_SIZE + (x + dir[1]*2);

        if (((board_turn[y3] >> x3) & 1) && 
            ((board_not_turn[y + dir[0]*2] >> (x + dir[1]*2)) & 1) && 
            ((board_not_turn[y + dir[0]] >> (x + dir[1])) & 1)) {
            pos[capture * 2] = bit1;
            pos[capture * 2 + 1] = bit2;
            capture++;
        }
    }

    return capture;
}