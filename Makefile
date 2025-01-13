CC = g++
CFLAGS = -Wall -O3 -fPIC -std=c++17
PYTHON = python3
TARGET = heuristic.cpython-*-x86_64-linux-gnu.so


all: $(TARGET)

$(TARGET): heuristic.cpp
	@$(PYTHON) setup.py build
	@cp build/lib*/$(TARGET) ./heuristic.so

clean:
	@rm -rf build/
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyc
	@rm -rf __pycache__/

run: $(TARGET)
	@$(PYTHON) main.py

fclean: clean
	@rm -f test_heuristic

test_heuristic:
	g++ -O3 -std=c++17 test_heuristic.cpp heuristic.cpp -o test_heuristic
	./test_heuristic

re: clean all

.PHONY: all clean run re