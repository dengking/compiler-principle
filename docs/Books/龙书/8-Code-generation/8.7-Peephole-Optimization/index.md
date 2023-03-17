# 8.7 Peephole Optimization 

While most production compilers produce good code through careful **instruction selection** and **register allocation**, a few use an alternative strategy: they generate naive code and then improve the quality of the target code by applying "optimizing" transformations to the target program. The term "optimizing" is somewhat misleading because there is no guarantee that the resulting code is optimal under any mathematical measure. Nevertheless, many simple transformations can signicantly improve the running time or space requirement of the target program.

A simple but effective technique for locally improving the target code is ***peephole optimization***, which is done by examining a **sliding window** of target instructions (called the **peephole**) and replacing instruction sequences within the peephole by a shorter or faster sequence, whenever possible. **Peephole optimization** can also be applied directly after **intermediate code generation** to improve the **intermediate representation**.

The peephole is a small, **sliding window** on a program. The code in the peephole need not be contiguous, although some implementations do require this. It is characteristic of **peephole optimization** that each improvement may spawn opportunities for additional improvements. In general, repeated passes over the target code are necessary to get the maximum benfiet. In this section, we shall give the following examples of program transformations that are characteristic of **peephole optimizations**: 

1、Redundant-instruction elimination 

2、Flow-of-control optimizations

3、Algebraic simplications

4、Use of machine idioms