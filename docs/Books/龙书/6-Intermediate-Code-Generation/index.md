# Chapter 6 Intermediate-Code Generation

> NOTE:
>
> 一、本章主要介绍的是将SDT用于type checking、intermediate-code generation: 
>
> Chapter 5:
>
> "The translation techniques in this chapter will be applied in Chapter 6 to **type checking** and **intermediate-code generation**."
>
> Chapter 6:
>
> "We shall use the syntax-directed formalisms of Chapters 2 and 5 to specify checking and translation"



In the **analysis-synthesis model** of a compiler, the **front end** analyzes a source program and creates an intermediate representation, from which the **back end** generates target code. Ideally, details of the source language are confined(限制于) to the **front end**, and details of the target machine to the **back end**. With a suitably defined intermediate representation, a compiler for language i and machine j can then be built by combining the **front end** for language i with the **back end** for machine j. This approach to creating suite of compilers can save a considerable amount of effort: `m * n` compilers can be built by writing just `m` front ends and `n` back ends.

This chapter deals with **intermediate representations**, **static type checking**, and **intermediate code generation**. For simplicity, we assume that a **compiler front end** is organized as in Fig. 6.1, where **parsing**, **static checking**, and **intermediate-code generation** are done sequentially; sometimes they can be combined and folded into **parsing**. We shall use the syntax-directed formalisms of Chapters 2 and 5 to specify checking and translation. Many of the translation schemes can be implemented during either bottom-up or top-down parsing, using the techniques of Chapter 5. All schemes can be implemented by creatinga syntax tree and then walking the tree.