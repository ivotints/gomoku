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

int new_minimax(move_t &move, bool turn, int alpha, int beta, int depth, int &total_evaluated)
{
    if (depth == 1 || move.eval < -100'000 || move.eval > 100'000) // means that it is a winning move
        return (move.eval);

    move_t moves[300];
    short move_count = 0;

    generate_all_legal_moves(move.boards[turn], move.boards[!turn], move.captures[turn], moves, &move_count); // at first i will implement old moves generator to test work of heuristic. then i will add new approach, whch will be fixed, without double threes bug.
    
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
            int eval = new_minimax(moves[i], !turn, alpha, beta, depth - 1, total_evaluated);
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
            int eval = new_minimax(moves[i], !turn, alpha, beta, depth - 1, total_evaluated);
            if (eval < best_eval)
            {
                beta = std::min(beta, eval);
                best_eval = eval;
                if (best_eval < -1'000'000)
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

    int current_board_eval = bitwise_heuristic(boards[0], boards[1], captures[0], captures[1]); // easier to get initial eval from it, and later to use star_heuristic. But we also can pass this value from gomoku class in python.

    std::cout << "current_board_eval: " << current_board_eval << std::endl;
    generate_all_legal_moves(boards[turn], boards[!turn], captures[turn], moves, &move_count);
    
    int total_evaluated = 0; // to count amount of boards evaluated.

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
            int eval = new_minimax(moves[i], !turn, -1'000'000, 1'000'000, depth, total_evaluated);
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
            int eval = new_minimax(moves[i], !turn, -1'000'000, 1'000'000, depth, total_evaluated);
            if (eval < best_eval)
            {
                best_move = moves[i].y * 19 + moves[i].x;
                best_eval = eval;
                if (best_eval < -100'000)
                    break;
            }
        }
    }
    std::cout << "Total evaluated: " << total_evaluated << std::endl;
    return {best_move, best_eval};
}
