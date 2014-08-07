CFLAGS+=--std=c99 -Werror -Wall -pedantic
#CFLAGS+=-g
CFLAGS+=-O3

SOURCES=$(wildcard src/*.c)
INCLUDES=$(wildcard src/*.h)

libmixupcube.so: $(SOURCES) $(INCLUDES)
	$(CC) -I./src/ $(CFLAGS) -fPIC -Wl,-soname,$@ --shared $(SOURCES) -o $@
