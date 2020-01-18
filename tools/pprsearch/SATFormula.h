#ifndef SATFORMULA_H
#define SATFORMULA_H

#include <vector>
#include <string>
#include <fstream>
#include <map>
#include <set>

#include <minisat/core/SolverTypes.h>

std::ostream & operator<<(std::ostream & out, Minisat::Lit l);
std::ostream & operator<<(std::ostream & out, std::vector<Minisat::Lit> c);

class SATFormula
{
public:
    typedef std::vector<Minisat::Lit> clause_t;

    enum UP { SAT, UNSAT, UNDEF };

    SATFormula();
    ~SATFormula();

    bool addClause(Minisat::Lit a) {
        clause_t tmp = { a };

        return addClause(tmp);
    }

    bool addClause(Minisat::Lit a, Minisat::Lit b) {
        clause_t tmp = { a, b };

        return addClause(tmp);
    }

    bool addClause(Minisat::Lit a, Minisat::Lit b, Minisat::Lit c) {
        clause_t tmp = { a, b, c };

        return addClause(tmp);
    }

    bool addClause(Minisat::Lit a, Minisat::Lit b, Minisat::Lit c, Minisat::Lit d) {
        clause_t tmp = { a, b, c, d };

        return addClause(tmp);
    }

    bool addClause(const clause_t & clause);

    size_t newVar() {
        return ++m_nVars;
    }

    size_t nVars() const {
        return m_nVars;
    }

    size_t nClauses() {
        return m_clauses.size();
    }

    static SATFormula fromDimacs(const std::string & filename) {
        std::ifstream file(filename);

        return fromDimacs(file);
    }

    static SATFormula fromDimacs(std::ifstream & file);

    void toDimacs(const std::string & filename) {
        std::ofstream file(filename);

        return toDimacs(file);
    }

    void toDimacs(std::ostream & file);

    bool setCompare(const SATFormula & other);

    void permute(const std::map<Minisat::Lit, Minisat::Lit> & perm);

    void simplify(const clause_t& assignment);

    UP unitPropagation(bool debug=false);

    Minisat::Var m_nVars;
    std::vector<clause_t> m_clauses;

private:
    std::set<std::set<Minisat::Lit>> toSet() const;
};

SATFormula::clause_t parseClause(std::string clauseLine);

#endif // SATFORMULA_H
