all: Keller-encode drat-trim/drat-trim tools/tautology cryptominisat-build/pycryptosat bliss-0.73 tools/pprsearch/pprsearch

CMSATBUILD=cryptominisat-build

Keller-encode: Keller-encode.c
	gcc -O2 -Wall Keller-encode.c -oKeller-encode

drat-trim/drat-trim: drat-trim/drat-trim.c
	gcc -O2 -Wall drat-trim/drat-trim.c -odrat-trim/drat-trim

tools/tautology: tools/tautology.c
	gcc -O2 -Wall tools/tautology.c -otools/tautology

cryptominisat-build/pycryptosat:
	mkdir -p ${CMSATBUILD}
	cd ${CMSATBUILD} && cmake ${CMAKEARGS} ../cryptominisat && make python_interface

bliss-0.73:
	wget http://www.tcs.hut.fi/Software/bliss/bliss-0.73.zip
	unzip bliss-0.73.zip
	cd bliss-0.73 && make lib

tools/pprsearch/pprsearch: bliss-0.73 cryptominisat-build/pycryptosat
	cd tools/pprsearch && g++ -o pprsearch -O2 pprsearch.cpp pprtools.cpp SATFormula.cpp ../../bliss-0.73/libbliss.a -I ../../${CMSATBUILD}/cmsat5-src/cryptominisat5 -I ../../bliss-0.73 -lboost_regex

clean:
	rm -f Keller-encode drat-trim/drat-trim tools/tautology tools/pprsearch/pprsearch
