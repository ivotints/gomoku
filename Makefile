CC = g++
CFLAGS = -Wall -O2 -march=native -flto -fPIC -shared -std=c++20  -pthread -Werror -Wextra

PYTHON = python3
TARGET = heuristic.so
SRC_DIR = src/
SRCS = $(addprefix $(SRC_DIR), bitwise_heuristic.cpp    new_minimax.cpp    moves_generator.cpp  move_generator.cpp   star_heuristic.cpp   zoristHash.cpp  utils.cpp  is_won.cpp)
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

fclean: clean
	@rm -rf .vscode/

re: clean all

.PHONY: all clean fclean run run2 re