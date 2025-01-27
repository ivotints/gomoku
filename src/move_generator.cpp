#include "gomoku.hpp"

void sort_moves(move_t (&moves)[300], short move_count, bool turn) {
    std::sort(moves, moves + move_count, [turn](const move_t &a, const move_t &b) {
            return (turn == BLACK) ? (a.eval > b.eval) : (a.eval < b.eval); // For BLACK: sort descending by eval, for WHITE: ascending
        }
    );
}

// If it found move x, y in moves, returns true
bool find_move(move_t* moves, uint8_t x, uint8_t y, short move_count) {
    for (short i = 0; i < move_count; i++)
        if (moves[i].x == x && moves[i].y == y)
            return true;
    return false;
}

// Used for initial generation of moves. Slow but simple.
void initial_move_generation(uint32_t (&boards)[2][19], move_t* moves, short* move_count)
{
    uint32_t union_board[19];
    uint32_t is_map_not_empty = 0;
   
    for(int i = 0; i < 19; i++) {  // first rewrite the board to union board.
        union_board[i] = boards[0][i] | boards[1][i];
        is_map_not_empty |= union_board[i];
    }
    if (is_map_not_empty == 0) { // check that map is not empty
        *move_count = 1;
        moves[0].y = 9;
        moves[0].x = 9;
        return ;
    }

    const char dir_vect[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}};
    *move_count = 0;
    for (int y = 0; y < 19; ++y) { // we will now search for piece in the board, if it is here, we generate moves around and add them to the list.
        for (int x = 0; x < 19; ++x) {
            if ((union_board[y] >> x) & 1) {  // if there is a stone, generate moves around (y, x)
                for (int d = 0; d < 8; ++d) {
                    int ny = y + dir_vect[d][0];
                    int nx = x + dir_vect[d][1];
                    if (nx < 0 || nx > 18 || ny < 0 || ny > 18) // out of map
                        continue;
                    if (((union_board[ny] >> nx) & 1)) // already on the map
                        continue; 
                    if (find_move(moves, nx, ny, *move_count)) // if move is in the list already
                        continue;
                   // we do not check for legality of move here, because later same move can become legal. We will check for legality before minimax call.
                    moves[*move_count].y = ny;
                    moves[*move_count].x = nx;
                    (*move_count)++;
                }
            }
        }
    }
}
