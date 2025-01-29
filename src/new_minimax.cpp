#include "gomoku.hpp"

inline void    light_move_generation(move_t *moves, short &move_count, move_t *moves_last, short move_count_last, move_t &move)
{
    for (short i = 0; i < move_count_last; ++i) // rewrite all possible moves from last generation of moves.
    {
        if (moves_last[i].x == move.x && moves_last[i].y == move.y) // not to add current move
            continue;
        moves[move_count].x = moves_last[i].x;
        moves[move_count].y = moves_last[i].y;
        move_count++;
    }

    const char dir_vect[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}}; //y, x //TODO can we put it into header? we have 3 copies of it. Repeating code...
    
    // now we need to generate 8 moves around current move
    for (uint8_t i = 0; i < 8; ++i)
    {
        int ny = move.y + dir_vect[i][0];
        int nx = move.x + dir_vect[i][1];
        if (nx < 0 || nx > 18 || ny < 0 || ny > 18) // out of map
            continue;
        if (((move.boards[0][ny] >> nx) & 1) || ((move.boards[1][ny] >> nx) & 1)) // if move is already on board
            continue;
        if (find_move(moves, nx, ny, move_count)) // if move is in the list already
            continue;
        // we do not check for legality of move here, because later same move can become legal. We will check for legality before minimax call.
        moves[move_count].y = ny;
        moves[move_count].x = nx;
        move_count++;
    }

    // // 8 more moves around instead of capture check
    // for (uint8_t i = 0; i < 8; ++i)
    // {
    //     int ny = move.y + 2 * dir_vect[i][0];
    //     int nx = move.x + 2 * dir_vect[i][1];
    //     if (nx < 0 || nx > 18 || ny < 0 || ny > 18) // out of map
    //         continue;
    //     if (((move.boards[0][ny] >> nx) & 1) || ((move.boards[1][ny] >> nx) & 1)) // if move is already on board
    //         continue;
    //     if (find_move(moves, nx, ny, move_count)) // if move is in the list already
    //         continue;
    //     // we do not check for legality of move here, because later same move can become legal. We will check for legality before minimax call.
    //     moves[move_count].y = ny;
    //     moves[move_count].x = nx;
    //     move_count++;
    // }

    if (move.capture_dir) // if we had a capture, we should generate move
    { 
        for (uint8_t dir_index = 0; dir_index < 8; ++dir_index)
        {
            if (move.capture_dir & (1 << dir_index)) // check capture
            {
                // it will be deffenetly not out of bounce,
                // it will not be in list already
                // there is obviously no piece in that place
                moves[move_count].x = move.x + 2 * dir_vect[dir_index][1];
                moves[move_count].y = move.y + 2 * dir_vect[dir_index][0];
                move_count++;
            }
        }
    }
}





int new_minimax(move_t &move, bool turn, int alpha, int beta, int depth, int &total_evaluated, move_t *moves_last, short move_count_last, u_int64_t *TTable)
{
    move_t moves[300];
    short move_count = 0;

    light_move_generation(moves, move_count, moves_last, move_count_last, move);

    for (short i = 0; i < move_count; ++i)
    {
        total_evaluated++;
        moves[i].eval = star_heuristic(move.boards, turn, move.captures, moves[i].y, moves[i].x, move.eval, moves[i].boards, moves[i].captures, moves[i].capture_dir);
        moves[i].hash = updateZobristHash(move.hash, moves[i].y, moves[i].x, turn, depth);
        // if (turn == BLACK) {
        //     if (moves[i].eval > 100'000) // mean that it found winning move
        //         return (moves[i].eval); }
        // else {
        //     if (moves[i].eval < -100'000)
        //         return (moves[i].eval); }
    }
    sort_moves(moves, move_count, turn); // now i need to sort them. i will call star_heuristc on every move and sort, depending on which turn is now. if turn is 0 that means we sort from biggrst to smallest.

    // std::cout << (turn ? "White" : "Black") << " turn, depth: "<< depth << "\n"; 
    // std::cout << "Moves amount: " << move_count << std::endl;
    // std::cout << "Move: x = " << (int)move.x << "\t" << "y = " << (int)move.y << "\n";
    // std::cout << "Board eval: " << move.eval << std::endl;
    // for (int i = 0; i < move_count; ++i)
    //     std::cout << "y = " << (int)moves[i].y << "\tx = " << (int)moves[i].x << "\tEval : " << moves[i].eval <<"\n";
    // std::cout << std::endl;


    int best_eval;
    if (turn == BLACK) // maximizing player
    {
        best_eval = -2'000'000;
        for (short i = 0; i < move_count; ++i) // for move in moves
        {
            if (!is_legal_lite(move.captures[turn], move.boards[turn], move.boards[!turn], moves[i].y, moves[i].x))// || isPositionVisited(TTable, moves[i].hash)) //changed to old boards
                continue;

            int eval = moves[i].eval;
            if (depth > 2 && eval > -100'000 && eval < 100'000) {
                eval = new_minimax(moves[i], !turn, alpha, beta, depth - 1, total_evaluated, moves, move_count, TTable);
            }

            if (eval > best_eval)
            {
                alpha = std::max(alpha, eval);
                best_eval = eval;
                if (best_eval > 100'000)
                    break;
            }
            if (beta <= alpha)
                break;
        }
    }
    else
    {
        best_eval = 2'000'000;
        for (short i = 0; i < move_count; ++i)
        {
            if (!is_legal_lite(move.captures[turn], move.boards[turn], move.boards[!turn], moves[i].y, moves[i].x))// || isPositionVisited(TTable, moves[i].hash))  //changed to old boards
                continue;

            int eval = moves[i].eval;
            if (depth > 2 && eval > -100'000 && eval < 100'000) {
                eval = new_minimax(moves[i], !turn, alpha, beta, depth - 1, total_evaluated, moves, move_count, TTable);
            }

            if (eval < best_eval)
            {
                beta = std::min(beta, eval);
                best_eval = eval;
                if (best_eval < -100'000)
                    break;
            }
            if (beta <= alpha)
                break;
        }
    }
    return (best_eval);
}



BotResult new_bot_play(uint32_t (&boards)[2][19], bool turn, uint8_t (&captures)[2], int depth)
{
    auto start = std::chrono::high_resolution_clock::now();
    initializeZobristTable();
    uint64_t *TTable = new uint64_t[300'000'000];
    move_t moves[300];
    short move_count = 0;

    int current_board_eval = bitwise_heuristic(boards[0], boards[1], captures[0], captures[1]); // easier to get initial eval from it, and later to use star_heuristic. But we also can pass this value from gomoku class in python.

    initial_move_generation(boards, moves, &move_count);
    int total_evaluated = 0; // to count amount of boards evaluated.

    for (short i = 0; i < move_count; ++i)
    {
        total_evaluated++;
        moves[i].eval = star_heuristic(boards, turn, captures, moves[i].y, moves[i].x, current_board_eval, moves[i].boards, moves[i].captures, moves[i].capture_dir);
        moves[i].hash = computeZobristHash(moves[i].boards[0], moves[i].boards[1], depth);
        // if (turn == BLACK) {
        //     if (moves[i].eval > 100'000) {
        //         delete[] TTable;
        //         return {(moves[i].y * 19 + moves[i].x), moves[i].eval}; }
        //     }
        // else {
        //     if (moves[i].eval < -100'000) {
        //         delete[] TTable;
        //         return {(moves[i].y * 19 + moves[i].x), moves[i].eval}; }
        //     }
    }
    sort_moves(moves, move_count, turn);

    // std::cout << "White_turn: " << move_count << std::endl;
    // std::cout << "Moves amount: " << move_count << std::endl;
    // std::cout << "Board eval: " << current_board_eval << std::endl;
    // for (int i = 0; i < move_count; ++i)
    //     std::cout << "y = " << (int)moves[i].y << "\tx = " << (int)moves[i].x << "\tEval : " << moves[i].eval <<"\n";
    // std::cout << std::endl;

    short best_move = moves[0].x + moves[0].y * 19;
    int best_eval = turn ? 2'000'000 : -2'000'000;

    for (short i = 0; i < move_count; ++i)
    {
        if (!is_legal_lite(captures[turn], boards[turn], boards[!turn], moves[i].y, moves[i].x))
            continue ;

        int eval = moves[i].eval;
        if (depth > 1 && ((turn && eval > -100'000) || (!turn && eval < 100'000))) {
            eval = new_minimax(moves[i], !turn, -1'000'000, 1'000'000, depth, total_evaluated, moves, move_count, TTable);
        }
        
        bool better_eval = turn ? (eval < best_eval) : (eval > best_eval);

        if (better_eval)
        {
            best_move = moves[i].y * 19 + moves[i].x;
            best_eval = eval;
            if ((turn && best_eval < -100'000) || (!turn && best_eval > 100'000))
                break;
        }
    }
    delete[] TTable;
    std::cout << "Total evaluated:   " << total_evaluated / 1000 << "'" << total_evaluated % 1000 << "\t";
    double duration = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
    std::cout << "Time taken: " <<  std::fixed << std::setprecision(3) << duration << "\t" << "Best eval: " << best_eval << "  \t" << "Move(y, x) " <<  best_move / 19 <<" "<< best_move % 19 << "\n";
    return {best_move, best_eval};
}
