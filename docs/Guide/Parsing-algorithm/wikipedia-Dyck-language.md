# [Dyck language](https://en.wikipedia.org/wiki/Dyck_language)



## Properties

- The Dyck language is closed under the operation of [concatenation](https://en.wikipedia.org/wiki/Concatenation).

- By treating $ \Sigma ^{*} $ as an algebraic [monoid](https://en.wikipedia.org/wiki/Monoid) under concatenation we see that the monoid structure transfers onto the [quotient](https://en.wikipedia.org/wiki/Quotient_monoid) $ \Sigma ^{*}/R $, resulting in the **[syntactic monoid](https://en.wikipedia.org/wiki/Syntactic_monoid) of the Dyck language**. The class $ \operatorname {Cl} (\epsilon ) $ will be denoted $ 1 $.

- The syntactic monoid of the Dyck language is not [commutative](https://en.wikipedia.org/wiki/Commutative): if $ u=\operatorname {Cl} ([) $ and $ v=\operatorname {Cl} (]) $ then $ uv=\operatorname {Cl} ([])=1\neq \operatorname {Cl} (][)=vu $.

- With the notation above, $ uv=1 $ but neither $ u $ nor $ v $ are invertible in $ \Sigma ^{*}/R $.

- The syntactic monoid of the Dyck language is isomorphic to the [bicyclic semigroup](https://en.wikipedia.org/wiki/Bicyclic_semigroup) by virtue of the properties of $ \operatorname {Cl} ([) $ and $ \operatorname {Cl} (]) $ described above.

- By the [Chomsky–Schützenberger representation theorem](https://en.wikipedia.org/wiki/Chomsky–Schützenberger_representation_theorem), any [context-free language](https://en.wikipedia.org/wiki/Context-free_language) is a homomorphic image of the intersection of some [regular language](https://en.wikipedia.org/wiki/Regular_language) with a Dyck language on one or more kinds of bracket pairs.

  > NOTE: 提过Dyck language，引入hierarchy。

- The Dyck language with two distinct types of brackets can be recognized in the [complexity class](https://en.wikipedia.org/wiki/Complexity_class) [$ TC^{0} $](https://en.wikipedia.org/wiki/TC0).[[2\]](https://en.wikipedia.org/wiki/Dyck_language#cite_note-2)

- The number of distinct Dyck words with exactly *n* pairs of parentheses is the *n*-th [Catalan number](https://en.wikipedia.org/wiki/Catalan_number).