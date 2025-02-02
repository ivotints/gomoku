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
    if (move.capture_dir) // if we had a capture, we should generate move
    {
        int8_t capture_dir = move.capture_dir;
        while (capture_dir)
        {
            int dir_index = __builtin_ctz(capture_dir);
            capture_dir &= ~(1 << dir_index);
            // it will be deffenetly not out of bounce,
            // it will not be in list already
            // there is obviously no piece in that place
            moves[move_count].x = move.x + 2 * dir_vect[dir_index][1];
            moves[move_count].y = move.y + 2 * dir_vect[dir_index][0];
            move_count++;
        }
    }
}


int new_minimax(move_t &move, bool turn, int alpha, int beta, int depth, std::atomic<int> &total_evaluated, move_t *moves_last, short move_count_last, table_t *TTable, int g_depth)
{
    move_t moves[300];
    short move_count = 0;

    light_move_generation(moves, move_count, moves_last, move_count_last, move);

    for (short i = 0; i < move_count; ++i)
    {
        total_evaluated++;
        moves[i].eval = star_heuristic(move.boards, turn, move.captures, moves[i].y, moves[i].x, move.eval, moves[i].boards, moves[i].captures, moves[i].capture_dir);
        moves[i].hash = updateZobristHash(move.hash, moves[i].y, moves[i].x, turn, depth, moves[i].capture_dir);

    }
    sort_moves(moves, move_count, turn); // now i need to sort them. i will call star_heuristc on every move and sort, depending on which turn is now. if turn is 0 that means we sort from biggrst to smallest.

    int moves_accepted = 0;
    int topX = std::max((depth * move_count) / 30, 3);

    int best_eval = turn ? 2'000'000 : -2'000'000;
    for (short i = 0; i < move_count; ++i)
    {
        if (!is_legal_lite(move.captures[turn], move.boards[turn], move.boards[!turn], moves[i].y, moves[i].x, moves[i].capture_dir))// || isPositionVisited(TTable, moves[i].hash)) //changed to old boards
            continue;
        int eval = moves[i].eval;

        if (depth < g_depth - 3 && moves_accepted >= topX)
        {
            break ;
        }
        else
        {
            moves_accepted++;
        }

        if (depth > 1 && eval > -100'000 && eval < 100'000)
               if (!isPositionVisited(TTable, moves[i].hash, eval)) {
                    eval = new_minimax(moves[i], !turn, alpha, beta, depth - 1, total_evaluated, moves, move_count, TTable, g_depth);
                     storePositionVisited(TTable, moves[i].hash, eval);
               }

        if (turn) // minimizig white
        {
            if (eval < best_eval)
            {
                beta = std::min(beta, eval);
                best_eval = eval;
                if (best_eval < -100'000)
                    break;
            }
        }
        else
        {
            if (eval > best_eval)
            {
                alpha = std::max(alpha, eval);
                best_eval = eval;
                if (best_eval > 100'000)
                    break;
            }
        }
        if (beta <= alpha)
            break;
    }
    return (best_eval);
}




constexpr size_t MAX_THREADS = 19;

static table_t* global_tables[MAX_THREADS] = {nullptr};
static bool tables_initialized = false;

void init_global_tables() {
    if (!tables_initialized) {
        for (size_t i = 0; i < MAX_THREADS; ++i) {
            global_tables[i] = new table_t[TABLE_SIZE]();
        }
        tables_initialized = true;
    }
}

BotResult new_bot_play(uint32_t (&boards)[2][19], bool turn, uint8_t (&captures)[2], int depth)
{
    auto start = std::chrono::high_resolution_clock::now();

    move_t moves[300];
    short move_count = 0;

    int current_board_eval = bitwise_heuristic(boards[0], boards[1], captures[0], captures[1]); // easier to get initial eval from it, and later to use star_heuristic. But we also can pass this value from gomoku class in python.

    initial_move_generation(boards, moves, &move_count);
    std::atomic<int> total_evaluated(0);

    for (short i = 0; i < move_count; ++i)
    {
        total_evaluated++;
        moves[i].eval = star_heuristic(boards, turn, captures, moves[i].y, moves[i].x, current_board_eval, moves[i].boards, moves[i].captures, moves[i].capture_dir);
        moves[i].hash = computeZobristHash(moves[i].boards[0], moves[i].boards[1], depth);

    }
    sort_moves(moves, move_count, turn);

    short best_move = moves[0].x + moves[0].y * 19;
    int best_eval = turn ? 2'000'000 : -2'000'000;
    unsigned int thread_count = std::thread::hardware_concurrency() - 1;
    std::vector<std::thread> threads;
    std::mutex best_move_mutex;
    std::atomic<int> i(0);
    for (unsigned int t = 0; t < thread_count; t++) {
        threads.emplace_back([&, t]() {
            while (true) {
                int current_i = i.fetch_add(1);
                if (current_i >= move_count) break;
                if (!is_legal_lite(captures[turn], boards[turn], boards[!turn],
                                   moves[current_i].y, moves[current_i].x, moves[current_i].capture_dir))
                    continue;
                int eval = moves[current_i].eval;
                if (depth > 1 && ((turn && eval > -100'000) || (!turn && eval < 100'000)))
                    eval = new_minimax(moves[current_i], !turn, -1'000'000, 1'000'000,
                                       depth - 1, total_evaluated, moves, move_count, global_tables[t], depth);
                {
                    std::lock_guard<std::mutex> lock(best_move_mutex);
                    bool better_eval = turn ? (eval < best_eval) : (eval > best_eval);
                    if (better_eval) {
                        best_move = moves[current_i].y * 19 + moves[current_i].x;
                        best_eval = eval;
                        if ((turn && best_eval < -100'000) || (!turn && best_eval > 100'000))
                            break;
                    }
                }
            }
        });
    }

    // for (short i = 0; i < move_count; ++i)
    // {
    //     if (!is_legal_lite(captures[turn], boards[turn], boards[!turn], moves[i].y, moves[i].x, moves[i].capture_dir))
    //         continue ;

    //     int eval = moves[i].eval;
    //     if (depth > 1 && ((turn && eval > -100'000) || (!turn && eval < 100'000))) {
    //         eval = new_minimax(moves[i], !turn, -1'000'000, 1'000'000, depth - 1, total_evaluated, moves, move_count, TTable, depth);
    //     }

    //     bool better_eval = turn ? (eval < best_eval) : (eval > best_eval);

    //     if (better_eval)
    //     {
    //         best_move = moves[i].y * 19 + moves[i].x;
    //         best_eval = eval;
    //         if ((turn && best_eval < -100'000) || (!turn && best_eval > 100'000))
    //             break;
    //     }
    // }
    for (auto &t : threads) {
        t.join();
    }
    std::cout << "Total evaluated:   " << total_evaluated / 1000 << "'" << total_evaluated % 1000 << "\t" << "Time taken: " <<  std::fixed << std::setprecision(3) << std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count() << "\t" << "Best eval: " << best_eval << "  \t" << "Move(y, x) " <<  best_move / 19 <<" "<< best_move % 19 << "\n";
        return {best_move, best_eval};
}
    // unsigned int thread_count = std::min(std::thread::hardware_concurrency() - 2, (unsigned int)move_count);
    // std::cout << "Thread count: " << thread_count << "\n";
    // std::vector<std::thread> threads;
    // std::mutex best_move_mutex;
    // std::atomic<int> i(0);
    // for (unsigned int t = 0; t < thread_count; t++) {
    //     threads.emplace_back([&, t]() {
    //         // init_thread_local_table();
    //         table_t *thread_local_table = new table_t[1]();
    //         while(true) {
    //             int current_i = i.fetch_add(1);
    //             if (current_i >= move_count) {
    //                 break;
    //             }
    //             if (!is_legal_lite(captures[turn], boards[turn], boards[!turn], moves[current_i].y, moves[current_i].x, moves[current_i].capture_dir))
    //                 continue;
    //             int eval = moves[current_i].eval;
    //             if (depth > 1 && ((turn && eval > -100'000) || (!turn && eval < 100'000)))
    //                 eval = new_minimax(moves[current_i], !turn, -1'000'000, 1'000'000, depth - 1, total_evaluated, moves, move_count, thread_local_table, depth);
    //             std::lock_guard<std::mutex> lock(best_move_mutex);
    //             bool better_eval = turn ? (eval < best_eval) : (eval > best_eval);

    //             if (better_eval)
    //             {
    //                 best_move = moves[current_i].y * 19 + moves[current_i].x;
    //                 best_eval = eval;
    //                 if ((turn && best_eval < -100'000) || (!turn && best_eval > 100'000))
    //                     break;
    //             }
    //         }
    //         delete[] thread_local_table;
    //         // cleanup_thread_local_table();
    //     });
    // }