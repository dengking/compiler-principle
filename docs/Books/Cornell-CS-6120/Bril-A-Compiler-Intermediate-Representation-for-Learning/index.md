# [Bril: A Compiler Intermediate Representation for Learning](https://capra.cs.cornell.edu/bril/intro.html)

Bril, the Big Red Intermediate Language, is a programming language for learning about compilers. It’s the intermediate representation we use in [CS 6120](https://www.cs.cornell.edu/courses/cs6120/2020fa/), a PhD-level compilers course. Bril’s design tenets include:

- Bril is an instruction-oriented language, like most good IRs.
- The core is minimal and ruthlessly regular. Extensions make it interesting.
  - 翻译: 核心部分极简纯粹，规则高度统一；各类扩展特性则让它变得丰富有趣。
- The tooling is language agnostic. Bril programs are just [JSON](https://www.json.org/).
  - 翻译: 这套工具链是语言无关的。
- Bril is typed.

See the [language reference](https://capra.cs.cornell.edu/bril/lang) for the complete language specification and the [tool documentation](https://capra.cs.cornell.edu/bril/tools) for details on the “batteries included” [monorepo](https://github.com/sampsyo/bril).

## [Language Reference](https://capra.cs.cornell.edu/bril/lang/index.html#language-reference)


