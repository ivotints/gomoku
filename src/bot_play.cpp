#include "gomoku.hpp"

CaptureResult check_capture(uint32_t* board_turn, uint32_t* board_not_turn, 
                              int y, int x) {
    const int BOARD_SIZE = 19;
    static std::vector<int> positions;  // Static to avoid reallocations
    positions.clear();
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
            capture++;
            positions.push_back(bit1);
            positions.push_back(bit2);
        }
    }

    CaptureResult result;
    result.capture_count = capture;
    result.position_count = positions.size();
    result.positions = positions.data();
    return result;
}

static inline bool is_winning_move(uint32_t* board_turn, uint32_t* board_not_turn,
                        int move, int turn, int capture) {
    int y = move / 19;
    int x = move % 19;
    
    CaptureResult cap = check_capture(board_turn, board_not_turn, y, x);
    if (cap.capture_count + capture > 4)
        return true;

    board_turn[y] |= (1u << x);
    bool is_win = has_winning_line(board_turn);
    board_turn[y] &= ~(1u << x);
    
    return is_win;
}

BotResult bot_play(uint32_t* board_turn, uint32_t* board_not_turn, bool turn, int* captures, int depth, short last_move, bool search) {
    static short moves_list[361];
    short *moves = moves_list;
    static int move_count_bot = 0;
    int move_count = 0;
    // std::cout << "played: " << last_move / 19 << ", " << last_move % 19 << std::endl;
    if (search)
        generate_all_legal_moves(board_turn, board_not_turn, captures[turn], moves, &move_count);
    else if (last_move == -1) {
        moves[0] = 9 * 19 + 9;
        move_count_bot = 1;
        move_count = 1;
    } else{
        find_and_remove(last_move, moves, &move_count_bot);
        generate_legal_moves(board_turn, board_not_turn, captures[turn], moves, &move_count_bot, last_move);
        move_count = move_count_bot;
    }
    // Check for winning moves first
    for (int i = 0; i < move_count; i++) {
        //std::cout << "move: " << moves[i] / 19 << ", " << moves[i] % 19 << std::endl;
        if (is_winning_move(board_turn, board_not_turn, moves[i], turn, captures[turn])) {
            return {moves[i], 1000000};
        }
    }

    struct MoveEval {
        short move;
        int eval;
    };
    
    std::vector<MoveEval> results(move_count);
    std::vector<std::thread> threads;
    // std::mutex best_move_mutex;

    std::srand(std::time(0));
    int best_move = moves[std::rand() % move_count];
    int best_eval = -1000000;

    // int num_threads = std::thread::hardware_concurrency();
    // int moves_per_thread = move_count / num_threads + 1; // or do it other way??
    int total_evaluated = 0;
    for (int i = 0; i < move_count; i++)
    {
        // int start = t * moves_per_thread;
        // int end = std::min((t + 1) * moves_per_thread, move_count);

        // threads.emplace_back([&, start, end]() {
        //     for (int i = start; i < end; i++) {
                int visited = 0;
                uint32_t new_board_turn[ROW_SIZE];
                uint32_t new_board_not_turn[ROW_SIZE];
                int new_captures[2] = {captures[0], captures[1]};

                memcpy(new_board_turn, board_turn, ROW_SIZE * sizeof(uint32_t));
                memcpy(new_board_not_turn, board_not_turn, ROW_SIZE * sizeof(uint32_t));

                int y = moves[i] / 19;
                int x = moves[i] % 19;
                CaptureResult capture = check_capture(new_board_turn, new_board_not_turn, y, x);
                new_board_turn[y] |= (1u << x);

                if (capture.capture_count > 0) {
                    new_captures[turn] += capture.capture_count;
                    for (int j = 0; j < capture.position_count; j++) {
                        int pos_y = capture.positions[j] / 19;
                        int pos_x = capture.positions[j] % 19;
                        new_board_not_turn[pos_y] &= ~(1u << pos_x);
                    }
                }

                int eval = minimax(new_board_not_turn, new_board_turn,
                                depth, -1000000, 1000000, false, !turn, new_captures, &visited, moves, move_count, moves[i]);
                results[i] = {moves[i], eval};
                // std::lock_guard<std::mutex> lock(best_move_mutex);
                total_evaluated += visited;
                if (eval > best_eval) {
                    best_eval = eval;
                    best_move = moves[i];
                }
            }

    // for (std::thread& thread : threads) {
    //     thread.join();
    // }
    if (!search)
        find_and_remove(best_move, moves, &move_count_bot);
    std::cout << "Total evaluated: " << total_evaluated << std::endl;
    // std::cout << "Best move: " << best_move / 19 << ", " << best_move % 19 << " with eval: " << best_eval << std::endl;
    return {best_move, best_eval};
}