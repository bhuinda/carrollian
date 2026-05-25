#ifndef MINISAT_LOCAL_COMPAT_H
#define MINISAT_LOCAL_COMPAT_H

#include <signal.h>
#include <cassert>

#ifndef SIGHUP
#define SIGHUP SIGTERM
#endif

#include "Alg.h"
#include "SolverTypes.h"

template<class V>
Clause* Clause_new(const V& ps, bool learnt);

#endif
