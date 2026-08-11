# Chapter 10 Instruction-Level Parallelism

Every **modern high‑performance processor** can execute several operations in a single **clock cycle**. The “billion‑dollar question” is how fast can a program be run on a processor with instruction‑level parallelism? The answer depends on:

1. The potential parallelism in the program.
2. The available parallelism on the processor.
3. Our ability to extract parallelism from the original sequential program.
4. Our ability to find the best **parallel schedule** given scheduling constraints.

If all the operations in a program are highly dependent upon one another, then no amount of hardware or parallelization techniques can make the program run fast in parallel. There has been a lot of research on understanding the limits of **parallelization**. Typical nonnumeric applications have many inherent dependences. For example, these programs have many data‑dependent branches that make it hard even to predict which instructions are to be executed, let alone decide which operations can be executed in parallel. Therefore, work in this area has focused on relaxing the scheduling constraints, including the introduction of new architectural features, rather than the scheduling techniques themselves.

翻译: 每一款现代高性能处理器都能够在单个时钟周期内执行多项运算。有一个备受业界关注的关键问题：在具备指令级并行能力的处理器之上，程序最快能够跑至多快？答案取决于四点：

1. 程序内部潜藏的并行度；
2. 处理器硬件能够提供的并行资源；
3. 我们能否从原始串行程序当中挖掘出并行；
4. 在调度约束之下，规划出最优并行调度方案。

倘若一个程序里所有运算之间都存在强依赖关系，那么无论配置多少硬件、采用何种并行优化技术，都难以让程序依靠并行加速运行。学界已经开展大量研究，用来探明程序并行化的上限。常规非数值类应用自带许多固有依赖。举例来说，这类程序存在大量数据相关分支，人们很难预判后续将要执行哪些指令，更不用说判定哪些运算可以并行运行。

所以该方向的研究重心大多放在放宽调度约束，例如增添全新硬件架构特性，而非单纯改进调度算法本身。

Numeric applications, such as scientific computing and signal processing, tend to have more parallelism. These applications deal with large aggregate data structures; operations on distinct elements in the structure are often independent of one another and can be executed in parallel. Additional hardware resources can take advantage of such parallelism and are provided in high‑performance, general‑purpose machines and digital signal processors. These programs tend to have simple control structures and regular data‑access patterns, and static techniques have been developed to extract the available parallelism from these programs. Code scheduling for such applications is interesting and significant, as they offer a large number of independent operations to be mapped onto a large number of resources.

Both parallelism extraction and scheduling for parallel execution can be performed either statically in software, or dynamically in hardware. In fact, even machines with hardware scheduling can be aided by software scheduling. This chapter starts by explaining the fundamental issues in using instruction‑level parallelism, which is the same regardless of whether the parallelism is managed by software or hardware. We then motivate the basic data‑dependence analyses needed for the extraction of parallelism. These analyses are useful for many optimizations other than instruction‑level parallelism as we shall see in Chapter 11.

Finally, we present the basic ideas in code scheduling. We describe a technique for scheduling basic blocks, a method for handling highly data‑dependent control flow found in general‑purpose programs, and finally a technique called software pipelining that is used primarily for scheduling numeric programs.


