#include <stdio.h>
#include <stdlib.h>

void pp (int i, int j, int d) {
  printf ("p(%i,%i,%i) ", i, j, d);
}

int main (int argc, char** argv) {

  for (int a = 0; a < 2; a++)
    for (int b = 0; b < 2; b++)
      for (int c = 0; c < a+2; c++)
        for (int d = 0; d < b+2; d++) {
          int emax = c+2;
          if (a+2 > emax) emax = a+2;
          for (int e = 0; e < emax; e++) {
            int fmax = d+2;
            if (b+2 > fmax) fmax = b+2;
            for (int f = 0; f < fmax; f++) {
              int gmax = e+2;
              if (a+2 > gmax) gmax = a+2;
              if (c+2 > gmax) gmax = c+2;
              for (int g = 0; g < gmax; g++) {
                int hmax = f+2;
                if (b+2 > hmax) hmax = b+2;
                if (d+2 > hmax) hmax = d+2;
                for (int h = 0; h < hmax; h++) {
                  if (a > b) continue;
                  if (a == b && c > d) continue;
                  if (a == b && c == d && e > f) continue;
                  if (a == b && c == d && e == f && g > h) continue;
                  pp (3, 2, a);
                  pp (3, 3, b);
                  pp (19, 2, c);
                  pp (19, 3, d);
                  pp (35, 2, e);
                  pp (35, 3, f);
                  pp (67, 2, g);
                  pp (67, 3, h);
                  printf ("0\n");
              }
            }
          }
        }
      }
}
