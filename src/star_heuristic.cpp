// old star_heuristic

#include "gomoku.hpp"

#define DIR_NW 1 << 0  // North-West
#define DIR_N  1 << 1  // North
#define DIR_NE 1 << 2  // North-East
#define DIR_E  1 << 3  // East
#define DIR_SE 1 << 4  // South-East
#define DIR_S  1 << 5  // South
#define DIR_SW 1 << 6  // South-West
#define DIR_W  1 << 7  // West

#define ALL_DIRS 0xFF        // All directions (255)
#define RIGHT_EDGE 0xE3      // DIR_NW | DIR_N | DIR_SW | DIR_S | DIR_W (227)
#define LEFT_EDGE 0x3C       // DIR_N | DIR_NE | DIR_E | DIR_SE | DIR_S (60)
#define BOTTOM_MIDDLE 0x8F   // DIR_NW | DIR_N | DIR_NE | DIR_E | DIR_W (143)
#define BOTTOM_RIGHT 0x83    // DIR_NW | DIR_N | DIR_W (131)
#define BOTTOM_LEFT 0x0E     // DIR_N | DIR_NE | DIR_E (14)
#define TOP_MIDDLE 0xFC      // DIR_E | DIR_SE | DIR_S | DIR_SW | DIR_W (252)
#define TOP_RIGHT 0xC0       // DIR_SW | DIR_S | DIR_W (192)
#define TOP_LEFT 0x38        // DIR_E | DIR_SE | DIR_S (56)

// takes a new boards, to which move will be made.
inline void make_a_move(uint32_t (&new_boards)[2][19], bool turn, uint8_t (&new_captures)[2], uint8_t y, uint8_t x, uint8_t &capture_dir)
{
    new_boards[turn][y] |= 1 << x; // set bit

    uint8_t directions;  // We will assign here directions that we will explore for capture

    if (y >= 3)
        if (y <= 15)
            if (x >= 3)
                if (x <= 15)
                    directions = ALL_DIRS; // Center area
                else
                    directions = RIGHT_EDGE; // Right edge
            else
                directions = LEFT_EDGE; // Left edge
        else
            if (x >= 3)
                if (x <= 15)
                    directions = BOTTOM_MIDDLE; // Bottom edge, middle x
                else
                    directions = BOTTOM_RIGHT; // Bottom-right corner
            else
                directions = BOTTOM_LEFT; // Bottom-left corner
    else
        if (x >= 3)
            if (x <= 15)
                directions = TOP_MIDDLE; // Top edge, middle x
            else
                directions = TOP_RIGHT; // Top-right corner
        else
            directions = TOP_LEFT; // Top-left corner

    const char dir_vect[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}}; //y, x

    for (uint8_t dir_index = 0; dir_index < 8; ++dir_index)
    {
        if (directions & (1 << dir_index)) // check if that direction exist
        {
            if (((new_boards[ turn][y + 3 * dir_vect[dir_index][0]] >> (x + 3 * dir_vect[dir_index][1])) & 1) &&
                ((new_boards[!turn][y + 2 * dir_vect[dir_index][0]] >> (x + 2 * dir_vect[dir_index][1])) & 1) &&
                ((new_boards[!turn][y +     dir_vect[dir_index][0]] >> (x +     dir_vect[dir_index][1])) & 1))
            {
                new_boards[!turn][y + 2 * dir_vect[dir_index][0]] &= ~(1 << (x + 2 * dir_vect[dir_index][1])); // if we here, mean that it is a capture.
                new_boards[!turn][y +     dir_vect[dir_index][0]] &= ~(1 << (x +     dir_vect[dir_index][1]));
                capture_dir |= (1 << dir_index);
                new_captures[turn]++;
            }
        }
    }
}


// Replace multiple __builtin_popcount calls with lookup table
static const uint8_t PopCountTable[32] = {
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5
};

inline void evaluate_line(uint32_t black_bits, uint32_t white_bits, int length, int &value) {
    for (int shift = 0; shift <= length - 5; ++shift) {
        uint32_t black_window = (black_bits >> shift) & 0b11111;
        uint32_t white_window = (white_bits >> shift) & 0b11111;

        if (!white_window) {
            int bits = PopCountTable[black_window];
            if (bits > 1) {
                value += (1 << (3 * (bits - 2)));
                if (bits == 5 && value < 100'000)
                    value += 1'000'000;
            }
        }

        if (!black_window) {
            int bits = PopCountTable[white_window];
            if (bits > 1) {
                value -= (1 << (3 * (bits - 2)));
                if (bits == 5 && value > -100'000)
                    value -= 1'000'000;
            }
        }
    }
}



// for black : patterns can be _BBW, where center can be in second or third B (negative reward),  or BWW_, _WWB (positive reward)

inline int check_potential_captures(uint8_t bits_black, uint8_t bits_white, uint8_t length, uint8_t center)
{
    int value = 0;

    // check which color is in the center
    bool black_center = (bits_black >> center) & 1;
    bool white_center = (bits_white >> center) & 1;

    const int potential_capture_value = white_center ? -4 : 4;

    if (white_center) //logic for black or white is same, so, not to repeat yourself, i do this
    {
        uint8_t tmp = bits_black;
        bits_black = bits_white;
        bits_white = tmp;
    }

    // now take a look at that. Here dispalyed all the possible combinations of length and center and all the possible patterns of white and balck.
    // ? means that we do not care what is there. this bit exist and can be measured, but we dont care
    // B means black bit
    // W means white bit
    // 0 means that here is no white, neither black bit.

    if (black_center || white_center)
    {
        // length 7, center 3 ???B???   ?0BbW??  ?WBb0??  ??0BBW?  ??WBB0?  0WWB???  ???BWW0  0WWBWW0

        // length 6, center 2 ???B??    ?0BBW?  ?WBB0?  ??0BBW  ??WBB0  0WWB??
        // length 6, center 3 ??B???    0BBW??  WBB0??  ?0BBW?  ?WBB0?  ??BWW0

        // length 5, center 1 ???B?     ?0BBW  ?WBB0  0WWB?
        // length 5, center 3 ?B???     0BBW?  WBB0?  ?BWW0

        // length 4, center 0 ???B      0WWB
        // length 4, center 3 B???      BWW0

        if (length == 7)
        {
            if (((bits_black >> 2) & 0b01111) == 0b0110) // apply mask for black  ?0BbW??  ?WBb0??
                if (((bits_white >> 2) & 0b1111) == 0b1000 || ((bits_white >> 2) & 0b1111) == 0b0001) // we found ?0BbW??  ?WBb0??
                    return (-potential_capture_value);
            if (((bits_black >> 1) & 0b01111) == 0b0110) // apply mask for black  ??0BBW?  ??WBB0?
                if (((bits_white >> 1) & 0b1111) == 0b1000 || ((bits_white >> 1) & 0b1111) == 0b0001) // we found ??0BBW?  ??WBB0?
                    return (-potential_capture_value);
            if (((bits_black >> 3) & 0b1111) == 0b0001) // 0WWB???
                if (((bits_white >> 3) & 0b1111) == 0b0110) // we found 0WWB???
                    value += potential_capture_value;
            if ((bits_black & 0b1111) == 0b1000) // ???BWW0
                if ((bits_white & 0b1111) == 0b0110) // we found ???BWW0
                    value += potential_capture_value;
            return (value);
        }

        // length 6, center 2 ???B??    ?0BBW?  ?WBB0?  ??0BBW  ??WBB0  0WWB??

        if (length == 6)
        {
            if (center == 2)
            {
                if (((bits_black >> 1) & 0b1111) == 0b0110) // ?0BBW?, ?WBB0?
                    if (((bits_white >> 1) & 0b1111) == 0b1000 || ((bits_white >> 1) & 0b1111) == 0b0001)
                        return (-potential_capture_value);
                if (((bits_black) & 0b1111) == 0b0110) // ??0BBW, ??WBB0
                    if (((bits_white) & 0b1111) == 0b1000 || ((bits_white) & 0b1111) == 0b0001)
                        return (-potential_capture_value);
                if (((bits_black >> 2) & 0b1111) == 0b0001) // 0WWB??
                    if (((bits_white >> 2) & 0b1111) == 0b0110)
                        return (potential_capture_value);
                return (0);
            }
            // length 6, center 3 ??B???    0BBW??  WBB0??  ?0BBW?  ?WBB0?  ??BWW0
            else // length == 6 and center == 3
            {
                if (((bits_black >> 2) & 0b1111) == 0b0110) // 0BBW??, WBB0??
                    if (((bits_white >> 2) & 0b1111) == 0b1000 || ((bits_white >> 2) & 0b1111) == 0b0001)
                        return (-potential_capture_value);
                if (((bits_black >> 1) & 0b1111) == 0b0110) // ?0BBW?  ?WBB0?
                    if (((bits_white >> 1) & 0b1111) == 0b1000 || ((bits_white >> 1) & 0b1111) == 0b0001)
                        return (-potential_capture_value);
                if ((bits_black & 0b1111) == 0b1000) // ??BWW0
                    if ((bits_white & 0b1111) == 0b0110)
                        return (potential_capture_value);
                return (0);
            }
        }

        // length 5, center 1 ???B?     ?0BBW  ?WBB0  0WWB?

        if (length == 5)
        {
            if (center == 1)
            {
                if (((bits_black) & 0b1111) == 0b0110) // ?0BBW, ?WBB0
                    if (((bits_white) & 0b1111) == 0b1000 || ((bits_white) & 0b1111) == 0b0001)
                        return (-potential_capture_value);
                if (((bits_black >> 1) & 0b1111) == 0b0001) // 0WWB?
                    if (((bits_white >> 1) & 0b1111) == 0b0110)
                        return (potential_capture_value);
                return (0);
            }

            // length 5, center 3 ?B???     0BBW?  WBB0?  ?BWW0

            else // center == 3
            {
                if (((bits_black >> 1) & 0b1111) == 0b0110) // 0BBW?, WBB0?
                    if (((bits_white >> 1) & 0b1111) == 0b1000 || ((bits_white >> 1) & 0b1111) == 0b0001)
                        return (-potential_capture_value);
                if ((bits_black & 0b1111) == 0b1000) // ?BWW0
                    if ((bits_white & 0b1111) == 0b0110)
                        return (potential_capture_value);
                return (0);
            }
        }

        // length 4, center 0 ???B      0WWB
        // length 4, center 3 B???      BWW0

        if (bits_white == 0b0110)
            if (bits_black == 0b0001 || bits_black == 0b1000)
                return (potential_capture_value);
    }
    else // center is 0
    {
        if (center + 3 < length) // BWW0
            if (((bits_black >> center) & 0b1111) == 0b1000)
                if (((bits_white >> center) & 0b1111) == 0b0110)
                    return (potential_capture_value);
        if (center + 3 < length) // WBB0
            if (((bits_white >> center) & 0b1111) == 0b1000)
                if (((bits_black >> center) & 0b1111) == 0b0110)
                    return (-potential_capture_value);
        if (center >= 3) // 0WWB
            if (((bits_black >> (center - 3)) & 0b1111) == 0b0001)
                if (((bits_white >> (center - 3)) & 0b1111) == 0b0110)
                    return (potential_capture_value);
        if (center >= 3) // 0BBW
            if (((bits_white >> (center - 3)) & 0b1111) == 0b0001)
                if (((bits_black >> (center - 3)) & 0b1111) == 0b0110)
                    return (-potential_capture_value);
    }
    return (0);
}




// it will output evaluation of the segment, with the center in that coordinates.
inline int star_eval(uint32_t (&boards)[2][19], int y, int x) {
    int left = std::min(4, x);
    int right = std::min(4, 18 - x);
    int up = std::min(4, y);
    int down = std::min(4, 18 - y);

    int value = 0;

    // Horizontal evaluation
    int start_x = x - left;
    int length_h = left + right + 1;
    uint32_t black_bits_h = (boards[BLACK][y] >> start_x) & ((1 << length_h) - 1);
    uint32_t white_bits_h = (boards[WHITE][y] >> start_x) & ((1 << length_h) - 1);
    evaluate_line(black_bits_h, white_bits_h, length_h, value);

    // Vertical evaluation
    int start_y = y - up;
    int length_v = up + down + 1;
    int black_bits_v = 0;
    int white_bits_v = 0;
    for(int i = 0; i < length_v; ++i)
    {
        black_bits_v |= ((boards[BLACK][start_y + i] >> x) & 1) << i;
        white_bits_v |= ((boards[WHITE][start_y + i] >> x) & 1) << i;
    }
    evaluate_line(black_bits_v, white_bits_v, length_v, value);

    // Diagonal (Top-Left to Bottom-Right) evaluation
    int diag_up = std::min(left, up);
    int diag_down = std::min(right, down);
    int start_diag_y = y - diag_up;
    int start_diag_x = x - diag_up;
    int length_d = diag_up + diag_down + 1;

    int black_bits_d = 0;
    int white_bits_d = 0;

    for(int i = 0; i < length_d; ++i)
    {
        black_bits_d |= ((boards[BLACK][start_diag_y + i] >> (start_diag_x + i)) & 1) << i;
        white_bits_d |= ((boards[WHITE][start_diag_y + i] >> (start_diag_x + i)) & 1) << i;
    }
    evaluate_line(black_bits_d, white_bits_d, length_d, value);

    // Anti-Diagonal
    int anti_up = std::min(right, up);
    int anti_down = std::min(left, down);
    int start_anti_y = y - anti_up;
    int start_anti_x = x + anti_up;
    int length_a = anti_up + anti_down + 1;

    int black_bits_a = 0;
    int white_bits_a = 0;

    for(int i = 0; i < length_a; ++i)
    {
        black_bits_a |= ((boards[BLACK][start_anti_y + i] >> (start_anti_x - i)) & 1) << i;
        white_bits_a |= ((boards[WHITE][start_anti_y + i] >> (start_anti_x - i)) & 1) << i;
    }
    evaluate_line(black_bits_a, white_bits_a, length_a, value);

    // here we will evaluate possible captures

    // first i need to extract 4 to 7 bits. if there not even 4 bits, capture is impossible and we skip.
    // we need that line of bits to run later for all 4 direction same logic.

    // we need that line of 7 bits, with additional number which indicates where is the middle
    // bits_black;       0001000
    // bits_white;       0110100
    // length;            7
    // center;            3 // signilase position from the right, count from 0
    // bits_black;       0001
    // bits_white;       0110
    // length;            4
    // center;            3 // signilase position from the right, count from 0

    int capture_value = 0;

    // Horizontal
    {
        int left_h = std::min(3, x);
        int right_h = std::min(3, 18 - x);
        uint8_t length_h = left_h + right_h + 1;

        uint8_t bits_black_h = (boards[BLACK][y] >> (x - left_h)) & ((1 << length_h) - 1);
        uint8_t bits_white_h = (boards[WHITE][y] >> (x - left_h)) & ((1 << length_h) - 1);

        if (length_h > 3)
            capture_value += check_potential_captures(bits_black_h, bits_white_h, length_h, left_h);
    }

    // Vertical
    {
        int up_v = std::min(3, y);
        int down_v = std::min(3, 18 - y);
        uint8_t bits_black_v = 0;
        uint8_t bits_white_v = 0;
        uint8_t length_v = up_v + down_v + 1;
        uint8_t center_v = up_v;

        for(int i = 0; i < length_v; i++) {
            bits_black_v |= ((boards[BLACK][y - up_v + i] >> x) & 1) << i;
            bits_white_v |= ((boards[WHITE][y - up_v + i] >> x) & 1) << i;
        }
        if (length_v > 3)
            capture_value += check_potential_captures(bits_black_v, bits_white_v, length_v, center_v);
    }

    // Diagonal
    {
        int up_d = std::min(3, std::min(x, y));
        int down_d = std::min(3, std::min(18 - x, 18 - y));
        uint8_t bits_black_d = 0;
        uint8_t bits_white_d = 0;
        uint8_t length_d = up_d + down_d + 1;
        uint8_t center_d = up_d;

        for(int i = 0; i < length_d; i++) {
            bits_black_d |= ((boards[BLACK][y - up_d + i] >> (x - up_d + i)) & 1) << i;
            bits_white_d |= ((boards[WHITE][y - up_d + i] >> (x - up_d + i)) & 1) << i;
        }
        if (length_d > 3)
            capture_value += check_potential_captures(bits_black_d, bits_white_d, length_d, center_d);
    }

    // Anti-diagonal
    {
        int up_a = std::min(3, std::min(18 - x, y));
        int down_a = std::min(3, std::min(x, 18 - y));
        uint8_t bits_black_a = 0;
        uint8_t bits_white_a = 0;
        uint8_t length_a = up_a + down_a + 1;
        uint8_t center_a = up_a;

        for(int i = 0; i < length_a; i++) {
            bits_black_a |= ((boards[BLACK][y - up_a + i] >> (x + up_a - i)) & 1) << i;
            bits_white_a |= ((boards[WHITE][y - up_a + i] >> (x + up_a - i)) & 1) << i;
        }
        if (length_a > 3)
            capture_value += check_potential_captures(bits_black_a, bits_white_a, length_a, center_a);
    }

    value += capture_value;

    return value;
}

int star_heuristic(uint32_t (&boards)[2][19], bool turn, uint8_t (&captures)[2], uint8_t y, uint8_t x, int eval, uint32_t (&new_boards)[2][19],  uint8_t (&new_captures)[2], uint8_t &capture_dir)
{
    new_captures[0] = captures[0];
    new_captures[1] = captures[1];

    // copy of boards
    memcpy(new_boards, boards, sizeof(uint32_t) * 2 * 19);

    capture_dir = 0; // each bit will represent direction of capture was made

    make_a_move(new_boards, turn, new_captures, y, x, capture_dir);

    const char dir_vect[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}}; //y, x
    for (uint8_t dir_index = 0; dir_index < 8; ++dir_index)
    {
        if (capture_dir & (1 << dir_index)) // check capture
        {
            // if we have a capture, we will run an additional star heuristics on each capture_pos.
            //this is worng logic. REWRITE! becaise same 5 bits will be evaluated 3 times.
            int old_eval = star_eval(boards, y + 2 * dir_vect[dir_index][0], x + 2 * dir_vect[dir_index][1]);
            old_eval += star_eval(boards, y + dir_vect[dir_index][0], x + dir_vect[dir_index][1]);
            int new_eval = star_eval(new_boards, y + 2 * dir_vect[dir_index][0], x + 2 * dir_vect[dir_index][1]);
            new_eval += star_eval(new_boards, y + dir_vect[dir_index][0], x + dir_vect[dir_index][1]);
            int delta_eval = new_eval - old_eval;
            eval += delta_eval;
        }
    }
    if (capture_dir)
    {
        int old_capture_eval = 16 << captures[turn];
        int new_capture_eval = 16 << new_captures[turn];
        int delta_captures_eval = new_capture_eval - old_capture_eval; // what if now not the black turn? should we minus that?
        if (new_captures[turn] > 4) // maybe we can delete captures[turn] <= 4 check
            delta_captures_eval += 1'000'000; // to indicate that it is winning.
        if (turn == BLACK)
            eval += delta_captures_eval;
        else
            eval -= delta_captures_eval;
    }
    // eval of last board - old eval of segment + new eval of segment
    //return (bitwise_heuristic(new_boards[0], new_boards[1], new_captures[0], new_captures[1]));
    return (eval + star_eval(new_boards, y, x) - star_eval(boards, y, x));
}
