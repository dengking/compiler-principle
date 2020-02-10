在《Compilers Principles, Techniques, & Tools Second Edition》4.2.4 Parse Trees and Derivations节中有这样的描述：

> A parse tree is a graphical representation of a derivation that filters out the **order** in which productions are applied to replace nonterminals. Each interior node of a parse tree represents the application of a production. The interior node is labeled with the nonterminal `A` in the head of the production; the children of the node are labeled, from left to right, by the symbols in the body of the production by which this `A` was replaced during the derivation.

expression tree的interior node是operator。

两者之间既存在着相同点也存在着不同点。

