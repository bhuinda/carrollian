#ifndef MINISAT_LOCAL_SYS_RESOURCE_H
#define MINISAT_LOCAL_SYS_RESOURCE_H

#include <sys/time.h>

#define RUSAGE_SELF 0

struct rusage {
  struct timeval ru_utime;
  struct timeval ru_stime;
  long ru_maxrss;
};

static inline int getrusage(int who, struct rusage *usage) {
  (void) who;
  if (usage) {
    usage->ru_utime.tv_sec = 0;
    usage->ru_utime.tv_usec = 0;
    usage->ru_stime.tv_sec = 0;
    usage->ru_stime.tv_usec = 0;
    usage->ru_maxrss = 0;
  }
  return 0;
}

#endif
