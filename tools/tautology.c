#include <stdio.h>
#include <stdlib.h>

int *clsList, *table, *sortable;

int compare (const void *p, const void *q) {
  int i = 0;

  for (;;) {
    if (table[i + *(int *)p] > table[i + *(int *)q]) return -1;
    if (table[i + *(int *)p] < table[i + *(int *)q]) return  1;
    i++; }
  return 0; }

int isPair (int a, int b) {
  int i;

  for (i = 0; ; i++) {
    if (sortable[clsList[a] + i] != sortable[clsList[b] + i]) {
      if ((sortable[clsList[a] + i] == -sortable[clsList[b] + i]) &&
          (sortable[clsList[a] + i + 1] == 0) &&
          (sortable[clsList[b] + i + 1] == 0))
        return i;
      return -1; } } }

int main (int argc, char** argv) {
  FILE* cnf;

  int tmp, nVar, nCls;

  cnf = fopen (argv[1], "r");
  tmp = fscanf (cnf, " p cnf %i %i ", &nVar, &nCls);

  if (tmp == 0) {
    printf ("p cnf line is missing\n");
    exit (0); }

  clsList = (int *) malloc (sizeof(int) * nCls);
  table   = (int *) malloc (sizeof(int) * nCls * 100);

  int lit = 0, inTable = 0, cls = 0;
  while (1) {
    if (lit == 0) clsList[cls++] = inTable;
    tmp = fscanf (cnf, " %i ", &lit);
    if (tmp == 0 || tmp == EOF) break;
    table[inTable++] = lit;
  }
  fclose (cnf);

  qsort (clsList, nCls, sizeof(int), compare);
  int i, j;

  sortable = (int*) malloc (sizeof(int) * inTable);

  inTable = 0;
  for (i = 0; i < nCls; i++) {
    int *copy = table + clsList[i];
    clsList[i] = inTable;
    while (*copy) sortable[inTable++] = *copy++;
    sortable[inTable++] = 0; }

  while (nCls > 1) {
   j = 0; inTable = 0;
   for (i = 0; i < nCls; i++) {
    int r;
    if (i == nCls - 1) r = -1;
    else r = isPair (i, i + 1);
    if (r != -1) {
      int k;
      i++;
      clsList[j++] = inTable;
      for (k = 0; k < r; k++) sortable[inTable++] = sortable[clsList[i] + k];
      sortable[inTable++] = 0;
    }
    else {
      int *copy = sortable + clsList[i];
      clsList[j++] = inTable;
      while (*copy) sortable[inTable++] = *copy++;
      sortable[inTable++] = 0;
    }
   }
   printf("c reducing nCls from %i to %i\n", nCls, j);
   if (nCls == j) break;
   nCls = j;
  }

  for (i = 0; i < nCls; i++) {
    printf("a ");
    int *copy = sortable + clsList[i];
    clsList[j++] = inTable;
    while (*copy) printf("%i ", *copy++);
    printf("0\n");
  }

}
