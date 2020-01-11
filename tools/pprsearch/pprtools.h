#ifndef PPRTOOLS_H
#define PPRTOOLS_H

#include "SATFormula.h"

bool check_ppr(const SATFormula&, const SATFormula::clause_t&, const SATFormula::clause_t&, const std::map<CMSat::Lit, CMSat::Lit>&);

std::map<CMSat::Lit, CMSat::Lit> search_permutation(const SATFormula&, const SATFormula::clause_t&, const SATFormula::clause_t&);

#endif // PPRTOOLS_H
