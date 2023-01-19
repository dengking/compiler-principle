# Chapter 7 Run-Time Environments

A compiler must accurately implement the **abstractions** embodied in the source-language definition. These abstractions typically include the concepts we discussed in Section 1.6 such as names, scopes, bindings, data types, operators,**procedures**, parameters, and flow-of-control constructs. The compiler must cooperate with the operating system and other systems software to support these **abstractions** on the target machine.

> NOTE: 上面这段话中的**abstractions**是有特殊含义的，参见文章[Abstraction](https://dengking.github.io/Post/Abstraction/Abstraction/)。
>
> Compiler需要使用[machine language](https://en.wikipedia.org/wiki/Machine_code)来实现programming language中的各种abstraction。

To do so, the compiler creates and manages a **run-time environment** in which it assumes its **target programs** are being executed. This environment deals with a variety of issues such as the layout and allocation of storage locations for the **objects** named in the source program, the mechanisms used by the target program to access **variables**, the linkages between procedures, the mechanisms for passing parameters, and the interfaces to the operating system, input/output devices, and other programs.

> NOTE: 显然，**run-time environment**是一个[概念模型](https://dengking.github.io/Post/Abstraction/Abstraction-and-model/)（是一个简化的模型，没有考虑multi-thread等），关于对这个概念模型的实现，参见工程[Linux-OS](https://dengking.github.io/Linux-OS/)的[Process mode: run time environment](https://dengking.github.io/Linux-OS/Kernel/Guide/Linux-OS's-multitasking/01-Process-mode-run-time-environment/)。
>
> 本段描述的这些内容是由[Application binary interface](https://en.wikipedia.org/wiki/Application_binary_interface)所约定。

The two themes in this chapter are **the allocation of storage locations** and **access to variables and data**. We shall discuss **memory management** in some detail, including **stack allocation**, **heap management**, and **garbage collection**. In the next chapter, we present techniques for generating target code for many common language constructs.

> NOTE: 本章的内容是比较重要的，因为process在运行过程中的主要活动都是发生在stack和heap。
>

