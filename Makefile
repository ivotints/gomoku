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

re: clean all

.PHONY: all clean run re