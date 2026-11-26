# B: Finding Linearly Independent Solutions


## 章首内容

Finding Linearly
Independent Solutions
Algorithm B.1 : Finds a maximal set of linearly independent solutions for
A~x ~0, and expresses them as rows of matrix B.
INPUT: An m n matrix A.
OUTPUT: A matrix B of linearly independent solutions to A~x ~0.
METHOD: The algorithm is shown in pseudocode below. Note that X[y] denotes the yth row of matrix X, X[y : z] denotes rows y through z of matrix X, and X[y : z][u : v] denotes the rectangle of matrix X in rows y through z and columns u through v. 2
T
M = A ;
r0 = 1;
c0 = 1;
B = In2n; /* an n-by-n identity matrix */ while ( true ) f
/* 1. Make M [r0 : r 1][c0 : c 1] into a diagonal matrix with positive diagonal entries and M [r : n][c0 : m] = 0.
M [r : n] are solutions. */ r = r0;
c = c ;
while ( there exists M [r][c] = 0 such that r r and c c are both 0 )
0 0 f
Move pivot M [r][c] to M [r ][c ] by row and column interchange;
Interchange row r with row r in B;
if ( M [r ][c ] < 0 ) f
M [r ] = 1 M [r ];
B[r ] = 1 B[r ];
g for ( row = r0 to n ) f if ( row = r and M [row][c ] = 0 )
6 6 f u = (M [row][c ]=M [r ][c ]);
M [row] = M [row] + u M [r ];
B[row] = B[row] + u B[r ];
g g r = r + 1;
c = c + 1;
g
/* 2. Find a solution besides M [r : n]. It must be a nonnegative combination of M [r0 : r 1][c0 : m] */
Find kr ; : : : ; kr001 0 such that kr M [r0][c : m] + + kr001M [r 1][c : m] 0;
if ( there exists a nontrivial solution, say kr > 0 ) f
M [r] = kr M [r0] + + kr001M [r 1];
NoMoreSoln = false;
g else /* M [r : n] are the only solutions */
NoMoreSoln = true;
/* 3. Make M [r0 : rn 1][c0 : m] 0 */ if ( NoMoreSoln ) /* Move solutions M [r : n] to M [r0 : rn 1] */ f 0 for ( r = r to n )
Interchange rows r and r0 + r r in M and B;
rn = r0 + n r + 1;
g else /* Use row addition to find more solutions */ f rn = n + 1;
for ( col = c to m ) if ( there exists M [row][col] < 0 such that row r0 ) if ( there exists M [r][col] > 0 such that r r0 ) f for ( row = r0 to rn 1 ) if ( M [row][col] < 0 ) f u = ( M [row][col]=M [r][col]) ;
d 0 e
M [row] = M [row] + u M [r];
B[row] = B[row] + u B[r];
g g else for ( row = rn 1 to r0 step -1 ) if ( M [row][col] < 0 ) f rn = rn 1;
Interchange M [row] with M [rn];
Interchange B[row] with B[rn];
g g
/* 4. Make M [r0 : rn 1][1 : c0 1] 0 */ for ( row = r0 to rn 1 ) for ( col = 1 to c0 1 ) if ( M [row][col] < 0 ) f
Pick an r such that M [r][col] > 0 and r < r0;
u = ( M [row][col]=M [r][col]) ;
d 0 e
M [row] = M [row] + u M [r];
B[row] = B[row] + u B[r];
g
/* 5. If necessary, repeat with rows M [rn : n] */ if ( NoMoreSoln or rn > n or rn = r0) f
Remove rows rn to n from B;
return B;
g else f cn = m + 1;
for ( col = m to 1 step -1 ) if ( there is no M [r][col] > 0 such that r < rn ) f cn = cn 1;
Interchange column col with cn in M ;
g r0 = rn;
c0 = cn;
g g
