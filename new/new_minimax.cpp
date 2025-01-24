#include "gomoku.hpp"
/* 
int minimax(position, depth, alpha, beta, maximizingPlayer)
	if depth == 0 or game over in position
		return static evaluation of position
 
	if maximizingPlayer
		maxEval = -infinity
		for each child of position
			eval = minimax(child, depth - 1, alpha, beta false)
			maxEval = max(maxEval, eval)
			alpha = max(alpha, eval)
			if beta <= alpha
				break
		return maxEval
 
	else
		minEval = +infinity
		for each child of position
			eval = minimax(child, depth - 1, alpha, beta true)
			minEval = min(minEval, eval)
			beta = min(beta, eval)
			if beta <= alpha
				break
		return minEval */

// other possibilities to sort.
/* inline void sift_up(move_t* moves, int pos, bool turn) {
    while (pos > 0) {
        int parent = (pos - 1) / 2;
        if (turn == BLACK) {
            if (moves[parent].eval >= moves[pos].eval) break;
        } else {
            if (moves[parent].eval <= moves[pos].eval) break;
        }
        std::swap(moves[parent], moves[pos]);
        pos = parent;
    }
} */
/* 
inline void sort_moves_insertion(move_t (&moves)[300], short move_count, bool turn)
{
    for (short i = 1; i < move_count; ++i) {
        move_t key = moves[i];
        short j = i - 1;
        while (j >= 0 && ((turn == BLACK && moves[j].eval < key.eval) || 
                          (turn == WHITE && moves[j].eval > key.eval))) {
            moves[j + 1] = moves[j];
            --j;
        }
        moves[j + 1] = key;
    }
} */


inline void sort_moves(move_t (&moves)[300], short move_count, bool turn)
{
    std::sort(moves, moves + move_count, [turn](const move_t &a, const move_t &b) {
            // For BLACK: sort descending by eval, for WHITE: ascending
            return (turn == BLACK) ? (a.eval > b.eval) : (a.eval < b.eval);
        }
    );
}







// returns true if it found move x, y in moves
inline bool find_move(move_t* moves, uint8_t x, uint8_t y, short move_count) {
    for (short i = 0; i < move_count; i++) {
        if (moves[i].x == x && moves[i].y == y) return true;
    }
    return false;
}





int new_minimax(move_t &move, bool turn, int alpha, int beta, int depth, int &total_evaluated, double &total_time, move_t *moves_last, short move_count_last)
{
    if (depth == 1 || move.eval < -100'000 || move.eval > 100'000) // means that it is a winning move
        return (move.eval);

    move_t moves[300];
    short move_count = 0;

    auto start = std::chrono::high_resolution_clock::now();

    for (short i = 0; i < move_count_last; ++i) // rewrite all possible moves from last generation of moves.
    {
        if (moves_last[i].x == move.x && moves_last[i].y == move.y) // not to add current move
            continue;
        moves[i].x = moves_last[i].x;
        moves[i].y = moves_last[i].y;
        move_count++;
    }
    // now we need to generate 8 moves around current move

    const char dir_vect[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}}; //y, x //TODO can we put it into header? we have 3 copies of it. Repeating code...

    for (uint8_t i = 0; i < 8; ++i)
    {
        if  (   move.x + dir_vect[i][1] > 18
            ||  move.x + dir_vect[i][1] < 0
            ||  move.y + dir_vect[i][0] > 18
            ||  move.y + dir_vect[i][0] < 0) // if move is not possible because it is out of bounce, we do not add it.
            continue;

        if (find_move(moves,  move.x + dir_vect[i][1], move.y + dir_vect[i][0], move_count)) // if move is in the list already, we do not add it.
            continue;
        
        if ((   move.boards[0][move.y + dir_vect[i][0]] >> (move.x + dir_vect[i][1]) & 1)
            || (move.boards[1][move.y + dir_vect[i][0]] >> (move.x + dir_vect[i][1]) & 1)) // if move is already on board
            continue;

        if (!is_legal_lite(move.captures[turn], move.boards[turn], move.boards[!turn],  move.y + dir_vect[i][0], move.x + dir_vect[i][1])) // if this move is illegal we do not add it
            continue;
        moves[move_count].x = move.x + dir_vect[i][1];
        moves[move_count].y = move.y + dir_vect[i][0];
        move_count++;
    }
    // later we will check if there was capture before. If so, we will generate move on capture made.
    // and also we will run checker for double three 7x7 area with center in x and y. star pattern. 
    
    //counter
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    total_time += duration.count();

    for (short i = 0; i < move_count; ++i)
    {
        total_evaluated++;
        moves[i].eval = star_heuristic(move.boards, turn, move.captures, moves[i].y, moves[i].x, move.eval, moves[i].boards, moves[i].captures);
        if (turn == BLACK) {
            if (moves[i].eval > 100'000) // mean that it found winning move
                return (moves[i].eval); }
        else {
            if (moves[i].eval < -100'000)
                return (moves[i].eval); }
    }
    sort_moves(moves, move_count, turn); // now i need to sort them. i will call star_heuristc on every move and sort, depending on which turn is now. if turn is 0 that means we sort from biggrst to smallest.

    int best_eval;
    if (turn == BLACK) // maximizing player
    {
        best_eval = -1'000'000;
        for (short i = 0; i < move_count; ++i) // for move in moves
        {
            int eval = new_minimax(moves[i], !turn, alpha, beta, depth - 1, total_evaluated, total_time, moves, move_count);
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
        best_eval = 1'000'000;
        for (short i = 0; i < move_count; ++i)
        {
            int eval = new_minimax(moves[i], !turn, alpha, beta, depth - 1, total_evaluated, total_time, moves, move_count);
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
    move_t moves[300];
    short move_count = 0;
    double total_time = 0.0;

    int current_board_eval = bitwise_heuristic(boards[0], boards[1], captures[0], captures[1]); // easier to get initial eval from it, and later to use star_heuristic. But we also can pass this value from gomoku class in python.

    //std::cout << "current_board_eval: " << current_board_eval << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    generate_all_legal_moves(boards[turn], boards[!turn], captures[turn], moves, &move_count);
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    int total_evaluated = 0; // to count amount of boards evaluated.
    total_time += duration.count();

    for (short i = 0; i < move_count; ++i)
    {
        total_evaluated++;
        moves[i].eval = star_heuristic(boards, turn, captures, moves[i].y, moves[i].x, current_board_eval, moves[i].boards, moves[i].captures);
        if (turn == BLACK) {
            if (moves[i].eval > 100'000) // mean that it found winning move
                return {(moves[i].y * 19 + moves[i].x), moves[i].eval}; }
        else {
            if (moves[i].eval < -100'000)
                return {(moves[i].y * 19 + moves[i].x), moves[i].eval}; }
    }
    sort_moves(moves, move_count, turn);

    short best_move = moves[0].x + moves[0].y * 19;

    int best_eval;
    if (turn == BLACK) // maximizing player
    {
        best_eval = -1'000'000;
        for (short i = 0; i < move_count; ++i) // for move in moves
        {
            int eval = new_minimax(moves[i], !turn, -1'000'000, 1'000'000, depth, total_evaluated, total_time, moves, move_count);
            if (eval > best_eval)
            {
                best_move = moves[i].y * 19 + moves[i].x;
                best_eval = eval;
                if (best_eval > 100'000)
                    break;
            }
        }
    }
    else
    {
        best_eval = 1'000'000;
        for (short i = 0; i < move_count; ++i)
        {
            int eval = new_minimax(moves[i], !turn, -1'000'000, 1'000'000, depth, total_evaluated, total_time, moves, move_count);
            if (eval < best_eval)
            {
                best_move = moves[i].y * 19 + moves[i].x;
                best_eval = eval;
                if (best_eval < -100'000)
                    break;
            }
        }
    }
    std::cout << "-----------------------------\n";
    std::cout << "Generate moves took: " << total_time / 1000'000 << " seconds\n";
    std::cout << "Total evaluated: " << total_evaluated / 1000 << "'" << total_evaluated % 1000 << std::endl;
    return {best_move, best_eval};
}
