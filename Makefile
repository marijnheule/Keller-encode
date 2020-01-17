BOOST_ROOT:=/usr

all: Keller-encode drat-trim/drat-trim tools/tautology tools/pprsearch/pprsearch tools/ppr2drat

minisat/minisat:
	git submodule update --init

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

tools/pprsearch/pprsearch: minisat/minisat bliss-0.73 tools/pprsearch/pprsearch.cpp tools/pprsearch/pprtools.cpp tools/pprsearch/pprtools.h tools/pprsearch/SATFormula.cpp tools/pprsearch/SATFormula.h
	cd tools/pprsearch && g++ -std=c++11 -o pprsearch -DNDEBUG -O2 pprsearch.cpp pprtools.cpp SATFormula.cpp ../../bliss-0.73/libbliss.a -I ../../minisat -I ../../bliss-0.73 -I${BOOST_ROOT}/include -L${BOOST_ROOT}/lib -lboost_regex

tools/ppr2drat: tools/ppr2drat.c
	cd tools && gcc -O2 -o ppr2drat ppr2drat.c

clean:
	rm -f Keller-encode drat-trim/drat-trim tools/tautology tools/pprsearch/pprsearch tools/ppr2drat

depclean: clean
	rm -rf bliss-0.73*

s3-python:
	python3 Keller.py 3 s3 ./Keller-encode tools/pprsearch/pprsearch tools/ppr2drat

s3-drat-trim:
	-drat-trim/drat-trim s3.cnf s3.drat -f
	-for drat in $(shell ls -1 s3.*.drat); do \
		cnffile="$$(basename $${drat} .drat).cnf"; \
		echo $${cnffile}; \
		drat-trim/drat-trim $${cnffile} $${drat} -f; \
	done

s3-tautology:
	nvars="$$(head -1 s3.cnf | awk '{ print $$3 }')"; \
	nclauses="$$(cat s3.dnf | wc -l)"; \
	echo "p cnf $${nvars} $${nclauses}" > s3-tautology.cnf
	sed 's/^a //' s3.dnf >> s3-tautology.cnf
	tools/tautology s3-tautology.cnf
	rm s3-tautology.cnf

s3: s3-python s3-drat-trim s3-tautology

s4-python:
	python3 Keller.py 4 s4 ./Keller-encode tools/pprsearch/pprsearch tools/ppr2drat

s4-drat-trim:
	-drat-trim/drat-trim s4.cnf s4.drat -f
	-for drat in $(shell ls -1 s4.*.drat); do \
		cnffile="$$(basename $${drat} .drat).cnf"; \
		echo $${cnffile}; \
		drat-trim/drat-trim $${cnffile} $${drat} -f; \
	done

s4-tautology:
	nvars="$$(head -1 s4.cnf | awk '{ print $$3 }')"; \
	nclauses="$$(cat s4.dnf | wc -l)"; \
	echo "p cnf $${nvars} $${nclauses}" > s4-tautology.cnf
	sed 's/^a //' s4.dnf >> s4-tautology.cnf
	tools/tautology s4-tautology.cnf
	rm s4-tautology.cnf

s4: s4-python s4-drat-trim s4-tautology

s6-python:
	python3 Keller.py 6 s6 ./Keller-encode tools/pprsearch/pprsearch tools/ppr2drat

s6-drat-trim:
	-drat-trim/drat-trim s6.cnf s6.drat -f
	-for drat in $(shell ls -1 s6.*.drat); do \
		cnffile="$$(basename $${drat} .drat).cnf"; \
		echo $${cnffile}; \
		drat-trim/drat-trim $${cnffile} $${drat} -f; \
	done

s6-tautology:
	nvars="$$(head -1 s6.cnf | awk '{ print $$3 }')"; \
	nclauses="$$(cat s6.dnf | wc -l)"; \
	echo "p cnf $${nvars} $${nclauses}" > s6-tautology.cnf
	sed 's/^a //' s6.dnf >> s6-tautology.cnf
	tools/tautology s6-tautology.cnf
	rm s6-tautology.cnf

s6: s6-python s6-drat-trim s6-tautology
