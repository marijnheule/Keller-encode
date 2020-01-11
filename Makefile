all: encode drattrim tautology pycryptominisat

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

clean:
	rm -f Keller-encode drat-trim/drat-trim tools/tautology
