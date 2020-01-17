#include "SATFormula.h"

#include <string>
#include <queue>
#include <map>
#include <iostream> // TODO delete
#include <regex>
#include <cassert>

#include <boost/algorithm/string.hpp>

std::ostream & operator<<(std::ostream & out, Minisat::Lit l) {
    return (out << (Minisat::sign(l) ? "-" : "") << Minisat::var(l));
}

std::ostream & operator<<(std::ostream & out, std::vector<Minisat::Lit> c) {
    for (auto l : c) {
        out << l << " ";
    }

    return (out << 0 << std::endl);
}

SATFormula::SATFormula() : m_nVars(0)
{
}

SATFormula::~SATFormula()
{
}

bool SATFormula::addClause(const std::vector<Minisat::Lit>& clause)
{
    for (auto l : clause) {
        if (Minisat::var(l) > m_nVars) {
            return false;
        }
    }

    m_clauses.push_back(clause);

    return true;
}

SATFormula SATFormula::fromDimacs(std::ifstream & file)
{
    SATFormula formula;
    size_t nclauses;
    std::string clauseLine;
    std::regex expression("^p\\s+cnf\\s+(\\d+)\\s+(\\d+)$");
    std::smatch m;

    std::getline(file, clauseLine);

#ifdef NDEBUG
    std::regex_match(clauseLine, m, expression);
#else
    assert(std::regex_match(clauseLine, m, expression));
#endif //NDEBUG

    formula.m_nVars = std::stoi(m[1]);
    formula.m_clauses.reserve(std::stol(m[2]));

    while (!file.eof())
    {
        std::getline(file, clauseLine);

        if (!clauseLine.empty() && (clauseLine[0] != 'c')) {
            std::vector<std::string> clauseVars;
            clause_t clause;

            boost::algorithm::split(clauseVars, clauseLine, boost::is_space());
            assert(clauseVars.back() == "0");
            clauseVars.pop_back();

            for (auto c : clauseVars) {
                if (c.length() == 0) {
                    continue;
                }

                int lval = std::stoi(c);

                clause.push_back(Minisat::mkLit(std::abs(lval), lval < 0));
            }

            formula.addClause(clause);
        }
    }

    return formula;
}

void SATFormula::toDimacs(std::ostream& file)
{
    file << "p cnf " << m_nVars << " " << m_clauses.size() << std::endl;

    for (auto c : m_clauses) {
        file << c;
    }

    return;
}

bool SATFormula::setCompare(const SATFormula & other)
{
    return toSet() == other.toSet();
}

void SATFormula::permute(const std::map<Minisat::Lit, Minisat::Lit> & perm)
{
    for (auto && c : m_clauses) {
        for (size_t i = 0; i < c.size(); i++) {
            if (perm.find(c[i]) != perm.end()) {
                c[i] = perm.at(c[i]);
            }
        }
    }

    return;
}

void SATFormula::simplify(const clause_t& assignment)
{
    for (auto & l : assignment) {
        m_clauses.erase(std::remove_if(m_clauses.begin(), m_clauses.end(), [l](const clause_t & c) {
            return std::find(c.begin(), c.end(), l) != c.end();
        }), m_clauses.end());

        for (auto & c : m_clauses) {
            auto neg = std::find(c.begin(), c.end(), ~l);

            if (neg != c.end()) {
                c.erase(neg);
            }
        }
    }
}

SATFormula::UP SATFormula::unitPropagation(bool debug)
{
    std::queue<Minisat::Lit> unitQueue;
    std::vector<Minisat::Lit> assignment;
    std::map<Minisat::Lit, std::vector<std::vector<clause_t>::iterator>> watches;
    bool foundEmpty = false;

    // First pass: populate the unitQueue and watches
    for (auto cit = m_clauses.begin(); cit != m_clauses.end(); cit++) {
        assert(!cit->empty());

        if (cit->size() > 1) {
            watches[cit->at(0)].push_back(cit);
            watches[cit->at(1)].push_back(cit);
        } else {
            unitQueue.push(cit->front());
        }
    }

    // Second pass: process the unitQueue
    while (!unitQueue.empty()) {
        auto l = unitQueue.front();

        unitQueue.pop();

        if (std::find(assignment.begin(), assignment.end(), l) == assignment.end()) {
            assignment.push_back(l);
        } else {
            continue;
        }

        for (auto& cit : watches[l]) {
            if (cit->at(1) == l) {
                std::iter_swap(cit->begin(), cit->begin() + 1);
            }
        }

        for (auto& cit : watches[~l]) {
            auto i = cit->begin() + 1;

            // Normalize so that we work on cit->front()
            if (cit->at(1) == ~l) {
                std::iter_swap(cit->begin(), cit->begin() + 1);
            }

            // Look for a replacement lit
            for (; i != cit->end(); i++) {
                if (std::find(assignment.begin(), assignment.end(), *i) != assignment.end()) {
                    // Clause is already satisfied
                    std::iter_swap(cit->begin(), i);
                    break;
                }
            }

            if (i == cit->end()) {
                for (i = cit->begin() + 2; i != cit->end(); i++) {
                    if (std::find(assignment.begin(), assignment.end(), ~(*i)) == assignment.end()) {
                        // *i is undefined so far
                        std::iter_swap(cit->begin(), i);
                        watches[cit->front()].push_back(cit);
                        break;
                    }
                }
            }

            if (i == cit->end()) {
                std::iter_swap(cit->begin(), cit->begin() + 1);

                if (std::find(assignment.begin(), assignment.end(), ~(cit->front())) == assignment.end()) {
                    unitQueue.push(cit->front());
                } else {
                    return UNSAT;
                }
            }
        }
    }

    if (debug) {
        std::cerr << "Assignment " << assignment;
    }

    // Cleanup satisfied clauses
    m_clauses.erase(std::remove_if(m_clauses.begin(), m_clauses.end(), [assignment](const clause_t& c) {
        return std::any_of(c.begin(), c.end(), [assignment](Minisat::Lit l) {
            return std::find(assignment.begin(), assignment.end(), l) != assignment.end();
        });
    }), m_clauses.end());

    if (m_clauses.empty()) {
        return SAT;
    }

    // Remove false literals from remaining clauses
    for (auto& c : m_clauses) {
        for (auto& l : assignment) {
            assert(std::find(c.begin(), c.end(), l) == c.end());
        }

        c.erase(std::remove_if(c.begin(), c.end(), [assignment](Minisat::Lit l) {
            return std::find(assignment.begin(), assignment.end(), ~l) != assignment.end();
        }), c.end());

        assert(c.size() != 1);
    }

    return UNDEF;
}

std::set<std::set<Minisat::Lit>> SATFormula::toSet() const
{
    std::set<std::set<Minisat::Lit>> clauses;

    for (auto & c : m_clauses) {
        std::set<Minisat::Lit> literals;

        for (auto & l : c) {
            literals.insert(l);
        }

        clauses.insert(literals);
    }

    return clauses;
}
