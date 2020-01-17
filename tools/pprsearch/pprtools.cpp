#include <graph.hh>

#include "SATFormula.h"

#include <iostream>

#include <boost/bimap.hpp>

SATFormula::clause_t negateClause(const SATFormula::clause_t & c)
{
    SATFormula::clause_t negated(c.size());

    std::transform(c.begin(), c.end(), negated.begin(), Minisat::operator~);

    return negated;
}

bool check_ppr(const SATFormula & formula, const SATFormula::clause_t & prclause, const SATFormula::clause_t & prwitness, const std::map<Minisat::Lit, Minisat::Lit> & p)
{
    SATFormula::clause_t alpha = negateClause(prclause);
    SATFormula falpha = formula;
    SATFormula fomega = formula;

    falpha.simplify(alpha);
    fomega.simplify(prwitness);
    fomega.permute(p);

    for (auto & c : fomega.m_clauses) {
        auto falphacopy = falpha;

        falphacopy.simplify(negateClause(c));

        if (falphacopy.unitPropagation() != SATFormula::UNSAT) {
            std::cerr << "Error adding clause " << prclause << "with witness " << prwitness;

            return false;
        }
    }

    return true;
}

boost::bimap<Minisat::Lit, unsigned int> incidenceGraph(bliss::Graph & g, const SATFormula & f)
{
    boost::bimap<Minisat::Lit, unsigned int>  lit2graph;
    std::set<Minisat::Var> liveVars;

    // First pass: detect what vars are still alive
    for (auto & c : f.m_clauses) {
        for (auto & l : c) {
            liveVars.insert(Minisat::var(l));
        }
    }

    // Create vertices for live literals
    for (auto & v : liveVars) {
        auto posLitVertex = g.add_vertex(0);
        auto negLitVertex = g.add_vertex(0);

        lit2graph.insert(boost::bimap<Minisat::Lit, unsigned int>::value_type(Minisat::mkLit(v, false), posLitVertex));
        lit2graph.insert(boost::bimap<Minisat::Lit, unsigned int>::value_type(Minisat::mkLit(v, true), negLitVertex));
        g.add_edge(posLitVertex, negLitVertex);
    }

    for (auto & c : f.m_clauses) {
        auto clauseVertex = g.add_vertex(1);

        for (auto & l : c) {
            g.add_edge(lit2graph.left.at(l), clauseVertex);
        }
    }

    return lit2graph;
}

bool isomorphism(const SATFormula& a, const SATFormula& b, std::map<Minisat::Lit, Minisat::Lit>& mapping)
{
    bliss::Graph galpha, gomega;
    bliss::Stats gstats;
    auto galphaMap = incidenceGraph(galpha, a);
    auto gomegaMap = incidenceGraph(gomega, b);
    auto galphaPermPtr = galpha.canonical_form(gstats, nullptr, nullptr);
    auto gomegaPermPtr = gomega.canonical_form(gstats, nullptr, nullptr);
    std::map<unsigned int, unsigned int> gomegaInverse;

    for (unsigned int i = 0; i < gomegaMap.right.size(); i++) {
        auto check = gomegaInverse.insert(std::make_pair(gomegaPermPtr[i], i));
        assert(check.second);
    }

    assert(gomegaInverse.size() == gomegaMap.right.size());

    auto galphaCanon = galpha.permute(galphaPermPtr);
    auto gomegaCanon = gomega.permute(gomegaPermPtr);
    bool isomorphic = galphaCanon->cmp(*gomegaCanon) == 0;
    mapping.clear();
    delete galphaCanon;
    delete gomegaCanon;

    if (isomorphic) {
        for (auto& i : galphaMap.left) {
            mapping[i.first] = gomegaMap.right.at(gomegaInverse.at(galphaPermPtr[i.second]));
        }
    }

    return isomorphic;
}

std::map<Minisat::Lit, Minisat::Lit> search_permutation(const SATFormula & formula, const SATFormula::clause_t & prclause, const SATFormula::clause_t & prwitness)
{
    SATFormula::clause_t alpha = negateClause(prclause);
    SATFormula falpha = formula;
    SATFormula fomega = formula;

    std::cerr << "Simplifying/propagating"  << std::endl;

    std::cerr << "falpha[before up]  : " << falpha.m_clauses.size() << " clauses" << std::endl;
    falpha.unitPropagation();
    std::cerr << "falpha[before simp]: " << falpha.m_clauses.size() << " clauses" << std::endl;
    falpha.simplify(alpha);
    std::cerr << "falpha[after simp] : " << falpha.m_clauses.size() << " clauses" << std::endl;
    std::cerr << "fomega[before up]  : " << fomega.m_clauses.size() << " clauses" << std::endl;
    fomega.unitPropagation();
    std::cerr << "fomega[before simp]: " << fomega.m_clauses.size() << " clauses" << std::endl;
    fomega.simplify(prwitness);
    std::cerr << "fomega[after simp] : " << fomega.m_clauses.size() << " clauses" << std::endl;

    // We need to search for a permutation
    std::map<Minisat::Lit, Minisat::Lit> permutation;

    std::cerr << "Checking isomorphism..." << std::endl;

#ifdef NDEBUG
    if (!isomorphism(fomega, falpha, permutation)) {
        std::cerr << "Error adding clause " << prclause << "with witness " << prwitness;
        std::abort();
    }
#else
    //TODO Figure out why is this triggered by unit clauses
    assert(isomorphism(fomega, falpha, permutation));
#endif // NDEBUG
    assert(isomorphism(fomega, falpha, permutation));

    std::cerr << "Graphs are isomorphic" << std::endl;

    fomega.permute(permutation);

    // Sanity check
    assert(falpha.setCompare(fomega));

    return permutation;
}
