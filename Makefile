all: encode

encode: Keller-encode.c
	gcc -O2 -Wall Keller-encode.c -oKeller-encode

clean:
	rm -f Keller-encode
