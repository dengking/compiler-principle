[Recursive descent parser](https://en.wikipedia.org/wiki/Recursive_descent_parser) use [backtracking](https://en.wikipedia.org/wiki/Backtracking) to match.

LL parsers are table-based parsers, they use parsing table. Parsing table is constructed from the grammar and acts as a transformation function. Using parsing table and *k* [tokens](https://en.wikipedia.org/wiki/Token_(parser)) of [lookahead](https://en.wikipedia.org/wiki/Parsing#Lookahead), a LL parser can become *predictive parser* and  avoid  [backtracking](https://en.wikipedia.org/wiki/Backtracking). 

