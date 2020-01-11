#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main (int argc, char** argv) {
  int i, nVar, nCls, opt = 0;

  FILE* cnf = fopen (argv[1], "r");
  if (cnf == NULL) {
    printf ("c ERROR parsing CNF formula %s\n", argv[1]);
    exit (0); }

  char comment[1024];

  size_t cllinelength = 0, maxcllinelength = 0;
  char * clline = NULL;
  while (!feof(cnf)) {
    getline(&clline, &cllinelength, cnf);
    if (cllinelength > maxcllinelength)
      maxcllinelength = cllinelength;
  }
  free(clline);
  fseek(cnf, 0, SEEK_SET);

  int tmp = fscanf (cnf, " p cnf %i %i ", &nVar, &nCls);
  while (tmp < 2) {
    tmp = fscanf (cnf, " %s ", comment);
    tmp = fscanf (cnf, " p cnf %i %i ", &nVar, &nCls); }

  // parse cnf
  int lit, var, nLit = 0, *formula;
  formula = (int*) malloc (sizeof (int) * maxcllinelength * nCls);
  while (1) {
    tmp = fscanf (cnf, " %i ", &lit);
    if (tmp == EOF) break;
    formula[nLit++] = lit; }

  fclose (cnf);

  if (argv[3] != NULL)
    if (argv[3][0] == '-' && argv[3][1] == 'O') opt = 1;

  FILE *pr  = NULL;
  if (strcmp(argv[2], "-") == 0)
    pr = stdin;
  else
    pr = fopen (argv[2], "r");
  if (pr == NULL) {
    printf ("c ERROR parsing PR proof %s\n", argv[2]);
    exit (0); }

  int *assignment, *map, *next;
  assignment  = (int*) malloc (sizeof (int) * (2*nVar + 1));
  map         = (int*) malloc (sizeof (int) * (2*nVar + 1));
  next        = (int*) malloc (sizeof (int) * (2*nVar + 1));
  assignment += nVar;
  map        += nVar;
  next       += nVar;
  int def = nVar + 1;
  int *lemma, lemma_size, *witness, witness_size, *perm, perm_size;

  lemma   = (int*) malloc (sizeof (int) * nVar);
  witness = (int*) malloc (sizeof (int) * nVar);
  perm    = (int*) malloc (sizeof (int) * nVar * 2);


  while (1) {
    tmp = fscanf (pr, " d %i ", &lit);
    if (tmp == EOF) break;

    int *p;
    int perm_count, piv, sat, red, mflag;

    // assignment and map reset... should become redundant
    for (i = 1; i <= nVar; i++) assignment[i] = assignment[-i] = 0;
    for (i = 1; i <= nVar; i++) { map[i] = next[i] = i; map [-i] = next[-i] = -i; }

    // if deletion step, then output step to stdout
    // and remove the clause from the formula.
    if (tmp > 0) {
      int toMatch = 1;
      if (abs(lit) > nVar) {
        printf ("c introduction of new variables in not supported\n");
        exit (0); }
      assignment[lit] = 1;
      printf ("d %i ", lit);
      while (lit) {
        tmp = fscanf (pr, " %i ", &lit);
        if (abs(lit) > nVar) {
          printf ("c introduction of new variables in not supported\n");
          exit (0); }
        if (lit != 0) printf ("%i ", lit), assignment[lit] = 1, toMatch++;
        else          printf ("0\n"); }

      int first = 0;
      for (i = 0; i < nLit; i++) {
        if (formula[i] == 0 && (i - first) == toMatch) {
          int k;
//          printf ("c deleting: "); for (k = first; k < i; k++) printf ("%i ", formula[k]); printf ("0\n");
          for (k = first; k < i; k++) formula[k] = 0;
          goto next_lemma; }
        if (assignment[formula[i]] != 1) {
          while (formula[i] != 0) i++;
          first = i + 1; } }
      goto next_lemma; }
    else { // parse lemma and potential witness and permutation
      int wflag    = 0;
      lemma_size   = 0;
      witness_size = 0;
      perm_size    = 0;
      tmp = fscanf (pr, " %i ", &lit);
      if (abs(lit) > nVar) {
        printf ("c introduction of new variables in not supported\n");
        exit (0); }
      int pivot    = lit;
      lemma[lemma_size++] = lit;
      while (lit) {
        tmp = fscanf (pr, " %i ", &lit);
        if (abs(lit) > nVar) {
          printf ("c introduction of new variables in not supported\n");
          exit (0); }
        if (lit == pivot) {
          wflag++;
          if (wflag == 1)               lemma  [  lemma_size++] = 0;
          if (wflag == 2)               witness[witness_size++] = 0;   }
        if (wflag == 0)                 lemma  [  lemma_size++] = lit;
        if (wflag == 1)                 witness[witness_size++] = lit;
        if (wflag == 2 && lit != pivot) perm   [   perm_size++] = lit; }

      // if no witness is provided, then the lemma should be DRAT already
      if (witness_size == 0) {
        p = lemma;
        while (*p) printf ("%i ", *p++);
        printf ("0\n");
        goto add_lemma; }


      int forced = 0, count = 0;

      tmp = nVar + 1;
      p = perm;
      while (*p) {
        tmp++;
        var = *p++; lit = *p++;
        next[ lit] =  tmp; next[-lit] = -tmp;
        map [ var] =  tmp; map [-var] = -tmp; }

      // phase I (a): print the weakened PR clause (NB: not in PR2DRAT)
      p = lemma; printf ("%i ", def); while (*p) printf ("%i ", *p++); printf ("0\n");

      // phase I (b): add shortened copies of clauses reduced, but not satisfied by omega
      if (perm_size) {
        // set the assignment to the lemma
        p = lemma; while (*p) { lit = *p++; assignment[ lit] = -2; assignment[-lit] =  2; }
        piv = 0, sat = 0, red = 0;
        for (i = 0; i < nLit; i++) {
          if (formula[i] == 0) {
            if ((sat == 0) && (red >  0)) {
              int k;
              printf ("%i ", -def);
              for (k = piv; k < i; k++)
                if (assignment[formula[k]] == 0)
                  printf ("%i ", formula[k]);
                printf("0\n"); }
            piv = i + 1; sat = 0; red = 0; }
          else if (assignment[formula[i]] >  0) sat++;
          else if (assignment[formula[i]] < -1) red++; }
        p = lemma; while (*p) { lit = *p++; assignment[ lit] = assignment[-lit] = 0; } }

      // phase I (c): add the full permutation definitions
      tmp = nVar + 1;
      p = perm;
      while (*p) {
        tmp++; var = *p++; lit = *p++;
        printf ("%i %i %i 0\n",  tmp, -var,  def);
        printf ("%i %i %i 0\n", -tmp,  var,  def);
        printf ("%i %i %i 0\n",  tmp, -lit, -def);
        printf ("%i %i %i 0\n", -tmp,  lit, -def); }

      // phase I (d): replace the above initial PR clause by the permutated one
      int flag = 0;
      p = lemma;   while (*p) { lit = *p++; if (map[lit] != lit) flag = 1; }
      if (flag) {
        p = lemma; printf (  "%i ", def); while (*p) printf ("%i ", map[*p++]); printf ("0\n");
        p = lemma; printf ("d %i ", def); while (*p) printf ("%i ",     *p++ ); printf ("0\n"); }

      // phase I (main): add shortened copies of clauses reduced, but not satisfied by omega
      piv = 0, sat = 0, red = 0;
      p = witness; while (*p) { lit = *p++; assignment[ lit] = 2; assignment[-lit] = -2; }
      for (i = 0; i < nLit; i++) {
        if (formula[i] == 0) {
          if ((sat == 0) && (red >  0)) {
            int k;
            printf ("%i ", -def);
            for (k = piv; k < i; k++)
              if (assignment[formula[k]] == 0) printf ("%i ", map[formula[k]]);
              printf("0\n"); }
          piv = i + 1; sat = 0; red = 0; }
        else if (assignment[formula[i]] >  0) sat++;
        else if (assignment[formula[i]] < -1) red++; }
      p = witness; while (*p) { lit = *p++; assignment[ lit] = assignment[-lit] =  0; }

      // phase I (z): clean up the clause additions in step I (b)
      if (perm_size) {
        piv = 0, sat = 0, red = 0;
        p = lemma; while (*p) { lit = *p++; assignment[ lit] = -2; assignment[-lit] =  2; }
        for (i = 0; i < nLit; i++) {
          if (formula[i] == 0) {
            if ((sat == 0) && (red >  0)) {
              int k;
              printf ("d %i ", -def);
              for (k = piv; k < i; k++)
                if (assignment[formula[k]] == 0) printf ("%i ", formula[k]);
                printf("0\n"); }
            piv = i + 1; sat = 0; red = 0; }
          else if (assignment[formula[i]] >  0) sat++;
          else if (assignment[formula[i]] < -1) red++; }
        p = lemma; while (*p) { lit = *p++; assignment[ lit] = assignment[-lit] =  0; } }


      // phase II (b): weaken the involved clauses
      piv = 0, sat = 0, red = 0;
      p = witness; while (*p) { lit = *p++; assignment[ lit] = 2; assignment[-lit] = -2; }
      for (i = 0; i < nLit; i++) {
        if (formula[i] == 0) {
          int k;
          if ((sat > 0) || (red > 0)) {
            if (sat == 0) {
              printf ("%i ", def);
              for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
              printf("0\n"); }
            if (sat > 0) printf ("%i ", def);
            for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
            printf("0\n");
            if (sat == 0) {
              printf ("d %i ", def);
              for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
              printf("0\n"); } }
          piv = i + 1; sat = 0; red = 0; }
        else if (assignment[formula[i]] >  0) sat++;
        else if (assignment[formula[i]] < -1) red++; }

      if (perm_size) {
        perm_count = 0; piv = 0; sat = 0; red = 0;
        for (i = 0; i < nLit; i++) {
          if (formula[i] == 0) {
            if ((sat == 0) && (red == 0) && (perm_count >  0)) {
              int k;
              printf ("%i ", def);
              for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
              printf("0\n");
              for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
              printf("0\n");
              printf ("d %i ", def);
              for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
              printf("0\n"); }
            piv = i + 1; sat = 0; red = 0; perm_count = 0; }
          else if (map[formula[i]] != formula[i]) perm_count++;
          else if (assignment[formula[i]] >  0) sat++;
          else if (assignment[formula[i]] < -1) red++; } }

      if (perm_size) {
        perm_count = 0; piv = 0; sat = 0; red = 0;
        for (i = 0; i < nLit; i++) {
          if (formula[i] == 0) {
            if ((sat > 0) || (red > 0) || (perm_count >  0)) {
            int k;
            printf ("d ");
            for (k = piv; k < i; k++) printf ("%i ", formula[k]);
            printf("0\n"); }
            piv = i + 1; sat = 0; red = 0; perm_count = 0; }
          else if (map[formula[i]] != formula[i]) perm_count++;
          else if (assignment[formula[i]] >  0) sat++;
          else if (assignment[formula[i]] < -1) red++; } }

      // phase II (a): add the implication x -> omega
      tmp = nVar + 1;
      p = perm;
      while (*p) {
        tmp++;
        var = *p++;
        lit = *p++;
        if (!assignment[var] && !assignment[lit]) continue;
        printf ("d %i %i %i 0\n",  var, -tmp,  def);
        printf ("d %i %i %i 0\n", -var,  tmp,  def);
        printf ("d %i %i %i 0\n",  lit, -tmp, -def);
        printf ("d %i %i %i 0\n", -lit,  tmp, -def); }

      p = witness; while (*p) printf ("%i %i 0\n", *p++, -def);

      tmp = nVar + 1;
      p = perm;
      while (*p) {
        tmp++;
        var = *p++;
        lit = *p++;
        if (assignment[var] || assignment[lit]) continue;
        printf ("d %i %i %i 0\n",  var, -tmp,  def);
        printf ("d %i %i %i 0\n", -var,  tmp,  def);
        printf ("d %i %i %i 0\n",  lit, -tmp, -def);
        printf ("d %i %i %i 0\n", -lit,  tmp, -def); }

      piv = 0, sat = 0, red = 0;
      for (i = 0; i < nLit; i++) {
        if (formula[i] == 0) {
          if ((sat == 0) && (red >  0)) {
            int k;
            printf ("d %i ", -def);
            for (k = piv; k < i; k++)
              if (assignment[formula[k]] == 0)
                printf ("%i ", map[formula[k]]);
              printf("0\n"); }
          piv = i + 1; sat = 0; red = 0; }
        else if (assignment[formula[i]] >  0) sat++;
        else if (assignment[formula[i]] < -1) red++; }

      // add the permutation without definition literals
      p = perm; tmp = nVar + 1;
      while (*p) {
        tmp++; var = *p++; lit = *p++;
        printf ("%i %i 0\n",  var, -tmp);
        printf ("%i %i 0\n", -var,  tmp); }

      // phase IV (b): strengthen the involved clauses
      piv = 0, sat = 0, red = 0;
      for (i = 0; i < nLit; i++) {
        if (formula[i] == 0) {
          if ((sat > 0) || (red >  0)) {
            int k;
            for (k = piv; k < i; k++) if (assignment[formula[k]] == 1) printf ("%i ", formula[k]);
            for (k = piv; k < i; k++) if (assignment[formula[k]] != 1) printf ("%i ", formula[k]);
            printf("0\nd ");
            if (sat > 0) printf ("%i ", def);
            for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
            printf("0\n"); }
          piv = i + 1; sat = 0; red = 0; }
        else if (assignment[formula[i]] >  0) sat++;
        else if (assignment[formula[i]] < -1) red++; }

      // map everything back to the orignial variables
      if (perm_size) {
        perm_count = 0; piv = 0; sat = 0; red = 0;

        // map back the weakened PR clause
        p = lemma; while (*p) { if (map[*p] != *p) perm_count++; p++; }
        if (perm_count) { perm_count = 0;
          p = lemma; printf (  "%i ", def); while (*p) printf ("%i ",     *p++ ); printf ("0\n");
          p = lemma; printf ("d %i ", def); while (*p) printf ("%i ", map[*p++]); printf ("0\n"); }

        // map back the original clauses
        for (i = 0; i < nLit; i++) {
          if (formula[i] == 0) {
            if ((sat == 0) && (red == 0) && (perm_count >  0)) {
            int k;
            for (k = piv; k < i; k++) printf ("%i ", formula[k]);
            printf("0\n");
            printf ("d ");
            for (k = piv; k < i; k++) printf ("%i ", map[formula[k]]);
            printf("0\n"); }
            piv = i + 1; sat = 0; red = 0; perm_count = 0; }
          else if (map[formula[i]] != formula[i]) perm_count++;
          else if (assignment[formula[i]] >  0) sat++;
          else if (assignment[formula[i]] < -1) red++; }

        // remove the permutation
        tmp = nVar + 1;
        p = perm;
        while (*p) {
          tmp++; var = *p++; lit = *p++;
          printf ("d %i %i 0\n",  tmp, -var);
          printf ("d %i %i 0\n", -tmp,  var); } }

      // phase IV (c): add the PR clause and remove the implication -> omega
      p = lemma;                        while (*p) printf ("%i ", *p++); printf ("0\n");
      p = lemma; printf ("d %i ", def); while (*p) printf ("%i ", *p++); printf ("0\n");
      p = witness; while (*p) { printf ("d %i %i 0\n", *(p++), -def); }

    add_lemma:;

    p = lemma;
    while (*p) formula[nLit++] = *p++;
    formula[nLit++] = 0; }

    next_lemma:;
  }

  if (pr != stdin)
    fclose(pr);
}
