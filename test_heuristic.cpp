#include <chrono>
#include <iostream>
#include <random>
#include <vector>
#include <fstream>
#include <signal.h>
#include <algorithm>
#include <deque>
#include "heuristic.h"

volatile bool running = true;

void generate_test_board(uint32_t* board, std::mt19937& gen) {
    std::uniform_int_distribution<uint32_t> dist(0, (1 << 19) - 1);
    for (int i = 0; i < 19; i++) {
        board[i] = dist(gen);
    }
}

void signal_handler(int signum) {
    running = false;
}

int main() {
    signal(SIGINT, signal_handler);
    
    std::ofstream log("heuristic_benchmark.txt", std::ios::app);
    const int BATCH_SIZE = 1'000'000;
    const int MIN_BATCHES = 5;  // Minimum batches for valid statistics
    std::deque<double> batch_times;  // Store last N batch times
    std::vector<uint32_t> board_turn(19);
    std::vector<uint32_t> board_not_turn(19);
    
    // Fixed test case
    std::mt19937 gen(43);
    const int capture = 2;
    const int capture_opponent = 2;
    generate_test_board(board_turn.data(), gen);
    generate_test_board(board_not_turn.data(), gen);

    uint64_t total_iterations = 0;

    log << "\n=== New benchmark session ===\n";
    std::cout << "Running benchmark (Ctrl+C to stop)...\n";

    while (running) {
        auto batch_start = std::chrono::high_resolution_clock::now();
        volatile int result = 0;
        bool batch_completed = true;
        
        for (int i = 0; i < BATCH_SIZE && running; i++) {
            result = bitwise_heuristic(
                board_turn.data(),
                board_not_turn.data(),
                capture,
                capture_opponent
            );
        }

        if (!running) {
            break;  // Don't count interrupted batch
        }

        auto batch_end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(batch_end - batch_start);
        double seconds = duration.count() / 1000000.0;
        
        batch_times.push_back(seconds);
        total_iterations += BATCH_SIZE;

        log << "Batch completed: " << BATCH_SIZE << " iterations in " << seconds 
            << "s (avg: " << (seconds * 1000000.0 / BATCH_SIZE) << " μs/call)\n";
        log.flush();
    }

    // Only calculate stats if we have enough complete batches
    if (batch_times.size() >= MIN_BATCHES) {
        double min_time = *std::min_element(batch_times.begin(), batch_times.end());
        double max_time = *std::max_element(batch_times.begin(), batch_times.end());
        double avg_time = std::accumulate(batch_times.begin(), batch_times.end(), 0.0) / batch_times.size();

        log << "\nFinal statistics (from " << batch_times.size() << " complete batches):\n"
            << "Min batch time: " << min_time << "s\n"
            << "Max batch time: " << max_time << "s\n"
            << "Average batch time: " << avg_time << "s\n"
            << "Average time per call: " << (avg_time * 1000000.0 / BATCH_SIZE) << " μs\n";
    }

    return 0;
}