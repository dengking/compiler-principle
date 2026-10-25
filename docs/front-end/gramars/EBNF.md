# Extended Backus–Naur form

wikipedia [Extended Backus–Naur form](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form)

| Usage                                                                                                                      | Notation  | Alternative | Meaning      |
| -------------------------------------------------------------------------------------------------------------------------- | --------- | ----------- | ------------ |
| definition                                                                                                                 | =         |             |              |
| [concatenation](https://en.wikipedia.org/wiki/Concatenation "Concatenation")                                               | ,         |             |              |
| termination                                                                                                                | ;         | .           |              |
| [alternation](https://en.wikipedia.org/wiki/Alternation_\(formal_language_theory\) "Alternation (formal language theory)") | \|        | / or !      |              |
| optional                                                                                                                   | [ ... ]   | (/ ... /)   | none or once |
| repetition                                                                                                                 | { ... }   | (: ... :)   | none or more |
| grouping                                                                                                                   | ( ... )   |             |              |
| terminal string                                                                                                            | " ... "   | ' ... '     |              |
| comment                                                                                                                    | (* ... *) |             |              |
| special sequence                                                                                                           | ? ... ?   |             |              |
| exception                                                                                                                  | -         |             |              |

## Examples

`term { '+' term }*` 是错误写法：`{ }` 已经表示重复，再加 `*` 是多余的。在 ISO EBNF 中 `*` 另有含义，例如 `3 * 'a'` 表示重复 3 次。