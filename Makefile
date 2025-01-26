CC = clang++
CFLAGS = -Wall -g -O3 -march=native -fPIC -shared -std=c++17  -pthread
PYTHON = python3
TARGET = heuristic.so
SRC_DIR = new/
SRCS = $(addprefix $(SRC_DIR), bitwise_heuristic.cpp    new_minimax.cpp    moves_generator.cpp   star_heuristic.cpp   zoristHash.cpp  utils.cpp  is_won.cpp)
BUILD_DIR = build/

all: $(TARGET)

$(TARGET): $(SRCS)
	@mkdir -p $(BUILD_DIR)
	@$(CC) $(CFLAGS) $^ -o $(BUILD_DIR)$@
	@cp $(BUILD_DIR)$@ ./

clean:
	@rm -rf $(BUILD_DIR)
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyc
	@rm -rf __pycache__/

run: $(TARGET)
	@$(PYTHON) main.py

run_with_help: $(TARGET)
	@$(PYTHON) main.py --suggest

run2: $(TARGET)
	@$(PYTHON) main.py -p 2

fclean: clean
	@rm -rf .vscode/

re: clean all

.PHONY: all clean fclean run run2 re