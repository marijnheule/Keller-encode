BOOST_ROOT:=/usr

all: Keller-encode drat-trim/drat-trim tools/tautology bliss-0.73 tools/pprsearch/pprsearch tools/ppr2drat

Keller-encode: Keller-encode.c
	gcc -O2 -Wall Keller-encode.c -oKeller-encode

drat-trim/drat-trim: drat-trim/drat-trim.c
	gcc -O2 -Wall drat-trim/drat-trim.c -odrat-trim/drat-trim

tools/tautology: tools/tautology.c
	gcc -O2 -Wall tools/tautology.c -otools/tautology

bliss-0.73:
	wget http://www.tcs.hut.fi/Software/bliss/bliss-0.73.zip
	unzip bliss-0.73.zip
	cd bliss-0.73 && make lib

tools/pprsearch/pprsearch: bliss-0.73
	cd tools/pprsearch && g++ -o pprsearch -DNDEBUG -O2 pprsearch.cpp pprtools.cpp SATFormula.cpp ../../bliss-0.73/libbliss.a -I ../../minisat -I ../../bliss-0.73 -I${BOOST_ROOT}/include -L${BOOST_ROOT}/lib -lboost_regex

tools/ppr2drat: tools/ppr2drat.c
	cd tools && gcc -O2 -o ppr2drat ppr2drat.c

clean:
	rm -f Keller-encode drat-trim/drat-trim tools/tautology tools/pprsearch/pprsearch tools/ppr2drat

depclean: clean
	rm -rf bliss-0.73*

s3:
	python3 Keller.py 3 s3 ./Keller-encode tools/pprsearch/pprsearch tools/ppr2drat >s3.drat 2>s3.dnf

s4:
	python3 Keller.py 4 s4 ./Keller-encode tools/pprsearch/pprsearch tools/ppr2drat >s4.drat 2>s4.dnf

s6:
	python3 Keller.py 3 s6 ./Keller-encode tools/pprsearch/pprsearch tools/ppr2drat >s6.drat 2>s6.dnf
