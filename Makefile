all: encode drattrim tautology pycryptominisat bliss-0.73

CMSATBUILD=cryptominisat-build

encode: Keller-encode.c
	gcc -O2 -Wall Keller-encode.c -oKeller-encode

drattrim: drat-trim/drat-trim.c
	gcc -O2 -Wall drat-trim/drat-trim.c -odrat-trim/drat-trim

tautology: tools/tautology.c
	gcc -O2 -Wall tools/tautology.c -otools/tautology

pycryptominisat:
	mkdir -p ${CMSATBUILD}
	cd ${CMSATBUILD} && cmake ${CMAKEARGS} ../cryptominisat && make python_interface

bliss-0.73:
	wget http://www.tcs.hut.fi/Software/bliss/bliss-0.73.zip
	unzip bliss-0.73.zip
	cd bliss-0.73 && make lib

clean:
	rm -f Keller-encode drat-trim/drat-trim tools/tautology
