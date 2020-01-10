all: encode drattrim

encode: Keller-encode.c
	gcc -O2 -Wall Keller-encode.c -oKeller-encode

drattrim: drat-trim/drat-trim.c
	gcc -O2 -Wall drat-trim/drat-trim.c -odrat-trim/drat-trim

clean:
	rm -f Keller-encode
