CC = g++
CFLAGS = -Wall -O3 -fPIC -shared -std=c++17  -pthread
PYTHON = python3
TARGET = heuristic.so
SRC_DIR = src/
SRCS = $(addprefix $(SRC_DIR), heuristic.cpp bot_play.cpp is_won.cpp moves_generator.cpp minimax.cpp)
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

run2: $(TARGET)
	@$(PYTHON) main.py -p 2

fclean: clean
	@rm -rf .vscode/

re: clean all

.PHONY: all clean fclean run run2 re