#ifndef PPRTOOLS_H
#define PPRTOOLS_H

#include "SATFormula.h"

bool check_ppr(const SATFormula&, const SATFormula::clause_t&, const SATFormula::clause_t&, const std::map<Minisat::Lit, Minisat::Lit>&);

std::map<Minisat::Lit, Minisat::Lit> search_permutation(const SATFormula&, const SATFormula::clause_t&, const SATFormula::clause_t&);

#endif // PPRTOOLS_H
