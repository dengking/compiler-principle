# 10 Instruction-Level Parallelism

- [10.1 Processor Architectures](10.1-Processor-Architectures.md)
- [10.2 Code-Scheduling Constraints](10.2-Code-Scheduling-Constraints.md)
- [10.3 Basic-Block Scheduling](10.3-Basic-Block-Scheduling.md)
- [10.4 Global Code Scheduling](10.4-Global-Code-Scheduling.md)
- [10.5 Software Pipelining](10.5-Software-Pipelining.md)
- [10.6 Summary of Chapter 10](10.6-Summary-of-Chapter-10.md)
- [10.7 References for Chapter 10](10.7-References-for-Chapter-10.md)

## 章首内容

Instruction-Level
Parallelism
Every modern high-performance processor can execute several operations in a single clock cycle. The \billion-dollar question" is how fast can a program be run on a processor with instruction-level parallelism? The answer depends on:
1. The potential parallelism in the program.
2. The available parallelism on the processor.
3. Our ability to extract parallelism from the original sequential program.
4. Our ability to find the best parallel schedule given scheduling constraints.
If all the operations in a program are highly dependent upon one another, then no amount of hardware or parallelization techniques can make the program run fast in parallel. There has been a lot of research on understanding the limits of parallelization. Typical nonnumeric applications have many inherent dependences. For example, these programs have many data-dependent branches that make it hard even to predict which instructions are to be executed, let alone decide which operations can be executed in parallel. Therefore, work in this area has focused on relaxing the scheduling constraints, including the introduction of new architectural features, rather than the scheduling techniques themselves.
Numeric applications, such as scientific computing and signal processing, tend to have more parallelism. These applications deal with large aggregate data structures; operations on distinct elements of the structure are often independent of one another and can be executed in parallel. Additional hardware resources can take advantage of such parallelism and are provided in highperformance, general-purpose machines and digital signal processors. These programs tend to have simple control structures and regular data-access patterns, and static techniques have been developed to extract the available parallelism from these programs. Code scheduling for such applications is interesting and significant, as they offer a large number of independent operations to be mapped onto a large number of resources.
Both parallelism extraction and scheduling for parallel execution can be performed either statically in software, or dynamically in hardware. In fact, even machines with hardware scheduling can be aided by software scheduling.
This chapter starts by explaining the fundamental issues in using instructionlevel parallelism, which is the same regardless of whether the parallelism is managed by software or hardware. We then motivate the basic data-dependence analyses needed for the extraction of parallelism. These analyses are useful for many optimizations other than instruction-level parallelism as we shall see in
Finally, we present the basic ideas in code scheduling. We describe a technique for scheduling basic blocks, a method for handling highly data-dependent control flow found in general-purpose programs, and finally a technique called software pipelining that is used primarily for scheduling numeric programs.
