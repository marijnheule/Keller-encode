#include <stdio.h>
#include <stdlib.h>

#define N	7
#define S	64

void pp (int i, int j, int d) {
  printf ("%i ", i * N * S + j * S + d + 1);
//  printf ("p(%i,%i,%i) ", i, j, d);
}

int main (int argc, char** argv) {

  int cube[28][6] = {
    {0,1,1,0,0,1},
    {0,1,1,0,1,1},
    {0,1,1,0,2,1},
    {0,1,1,1,0,0},
    {0,1,1,1,0,2},
    {0,1,1,1,1,0},
    {0,1,1,1,1,1},
    {0,1,1,1,1,2},
    {0,1,1,1,2,0},
    {0,1,1,1,2,1},
    {0,1,1,1,2,2},
    {0,1,1,2,1,1},
    {0,1,1,2,2,1},
    {1,1,0,0,1,1},
    {1,1,0,0,2,1},
    {1,1,0,2,1,1},
    {1,1,0,2,2,1},
    {1,1,1,1,1,1},
    {1,1,1,1,1,2},
    {1,1,1,1,2,2},
    {1,1,1,2,2,1},
    {1,1,2,0,2,1},
    {1,1,2,0,3,1},
    {1,1,2,1,2,1},
    {1,1,2,1,2,2},
    {1,1,2,1,3,1},
    {1,1,2,1,3,2},
    {2,1,1,2,2,1}
  };


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

                  for (int i = 0; i < 28; i++) {
                    printf ("a ");

                    pp (3, 2, a);
                    pp (3, 3, b);
                    pp (19, 2, c);
                    pp (19, 3, d);
                    pp (35, 2, e);
                    pp (35, 3, f);
                    pp (67, 2, g);
                    pp (67, 3, h);


                    pp (19, 6, cube[i][0]);
                    pp (19, 7, cube[i][1]);
                    pp (35, 5, cube[i][2]);
                    pp (35, 7, cube[i][3]);
                    pp (67, 5, cube[i][4]);
                    pp (67, 6, cube[i][5]);

                    printf ("0\n");
                  }
              }
            }
          }
        }
      }
}
