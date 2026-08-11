# 8.2 The Target Language

Familiarity with the target machine and its **instruction set** is a prerequisite for designing a good **code generator**. Unfortunately, in a general discussion of code generation it is not possible to describe any **target machine** in sufficient detail to generate good code for a complete language on that machine. In this chapter, we shall use as a **target language assembly code** for a simple computer that is representative of many register machines. However, the code‑generation techniques presented in this chapter can be used on many other classes of machines as well.

翻译: 熟悉目标机器及其指令集，是设计出优秀代码生成器的先决条件。遗憾的是，在对代码生成进行通用性讲解时，我们无法详尽描述某一台目标机器的全部细节，从而为整套编程语言在该设备上产出优质目标代码。本章选用一台简易寄存器型计算机的汇编语言作为目标语言，该机型可以代表绝大多数寄存器架构机器。与此同时，本章介绍的各类代码生成技术同样适用于其余多种硬件机型。

## 8.2.1 A Simple Target Machine Model

Our target computer models a **three‑address machine** with load and store operations, **computation operations**, **jump operations**, and **conditional jumps**. The underlying computer is a byte‑addressable machine with $n$ general‑purpose registers, R0, R1, … , Rn − 1. 

A full‑fledged assembly language would have scores of instructions. To avoid hiding the concepts in a myriad of details, we shall use a very limited set of instructions and assume that all operands are integers. Most instructions consists of an operator, followed by a target, followed by a list of source operands. A label may precede an instruction. We assume the following kinds of instructions are available:

### Load operations

**Load operations**: The instruction `LD dst, addr` loads the value in location `addr` into location `dst`. This instruction denotes the assignment `dst = addr`. The most common form of this instruction is `LD r, x` which loads the value in location $x$ into register $r$. An instruction of the form `LD r1, r2` is a ***register‑to‑register copy*** in which the contents of register $r_2$ are copied into register $r_1$.

### Store operations

**Store operations**: The instruction `ST x, r` stores the value in register $r$ into the location $x$. This instruction denotes the assignment $x = r$.

### Computation operations

**Computation operations** of the form `OP dst, src₁, src₂`, where $OP$ is an operator like ADD or SUB, and dst, $src_1$, and $src_2$ are locations, not necessarily distinct. The effect of this machine instruction is to apply the operation represented by $OP$ to the values in locations $src_1$ and $src_2$, and place the result of this operation in location dst. For example, `SUB r1, r2, r3` computes $r_1 = r_2 - r_3$. Any value formerly stored in $r_1$ is lost, but if $r_1$ is $r_2$ or $r_3$, the old value is read first. Unary operators that take only one operand do not have a $src_2$.

### Unconditional jumps

**Unconditional jumps**: The instruction `BR L` causes control to branch to the machine instruction with label L. (BR stands for branch.)

### Conditional jumps

**Conditional jumps** of the form `Bcond r, L`, where r is a register, L is a label, and cond stands for any of the common tests on values in the register r. For example, `BLTZ r, L` causes a jump to label L if the value in register r is less than zero, and allows control to pass to the next machine instruction if not.




### Addressing modes

We assume our target machine has a variety of addressing modes:

#### variable name

In instructions, a location can be a variable name $x$ referring to the memory location that is reserved for $x$ (that is, the l‑value of $x$).

#### indexed address of variable(变址寻址) + register

A location can also be an indexed address of the form $a(r)$, where $a$ is a variable and $r$ is a register. The memory location denoted by $a(r)$ is computed by taking the l‑value of $a$ and adding to it the value in register $r$. For example, the instruction `LD R1, a(R2)` has the effect of setting $\text{R1} = \text{contents}(a+\text{contents(R2)})$, where $\text{contents}(x)$ denotes the contents of the register or memory location represented by $x$. This addressing mode is useful for accessing arrays, where $a$ is the base address of the array (that is, the address of the first element), and $r$ holds the number of bytes past that address we wish to go to reach one of the elements of array $a$.

翻译: 存储位置同样可以采用形如 $a(r)$ 的变址寻址地址，其中 $a$ 为变量，$r$ 代表寄存器。
$a(r)$ 对应的内存地址求解方式：取出 $a$ 的左值（内存地址），再加上寄存器 $r$ 内部存储的数值。举个例子，指令 `LD R1, a(R2)` 的执行效果等价于
$\text{R1} = \text{contents}(a+\text{contents(R2)})$；
函数 $\text{contents}(x)$ 代表读取 $x$ 所指向寄存器或者内存单元当中存放的数据。
该寻址方式十分适合数组访问场景：$a$ 是数组的基地址（数组首个元素的地址），寄存器 $r$ 保存目标元素距离数组首地址的字节偏移量，借此定位数组 $a$ 的任意元素。



#### integer indexed by a register(变址寻址)

A memory location can be an integer(立即数) indexed by a register. For example, `LD R1, 100(R2)` has the effect of setting $\text{R1} = \text{contents}(100+\text{contents(R2)})$, that is, of loading into R1 the value in the memory location obtained by adding 100 to the contents of register R2. This feature is useful for following pointers, as we shall see in the example below.

译文: 内存地址可以是一个整数搭配寄存器偏移的变址形式。例如指令 `LD R1, 100(R2)`，执行逻辑为 $\text{R1} = \text{contents}(100+\text{contents(R2)})$，也就是将寄存器 R2 的数值加上立即数100，读取该内存单元的数据并载入寄存器R1。后文示例将会讲到，此种寻址方式非常适合指针寻址操作。



#### indirect addressing modes(间接寻址模式)

We also allow two **indirect addressing modes**: 

- `*r` means the memory location found in the location represented by the contents of register $r$  

- `*100(r)` means the memory location found in the location obtained by adding 100 to the contents of $r$. 

For example, `LD R1, *100(R2)` has the effect of setting $\text{R1} = \text{contents}(\text{contents}(100+\text{contents(R2)}))$, that is, of loading into R1 the value in the memory location stored in the memory location obtained by adding 100 to the contents of register R2.

翻译: 本机还支持两种**间接寻址模式**：
`*r` 代表先取出寄存器 $r$ 的存储值当作内存地址，再访问该地址对应的内存单元；
`*100(r)` 为先将寄存器 $r$ 内的值加上立即数100得到内存地址，再读取该地址里存放的地址，最终访问此二次寻址对应的内存单元。
举例而言，指令 `LD R1, *100(R2)` 的执行效果：
$\text{R1} = \text{contents}(\text{contents}(100+\text{contents(R2)}))$
通俗来讲：寄存器R2的值加上100得到地址A；读取地址A当中保存的地址B；最后把地址B存储的数据加载至寄存器R1。



#### immediate constant addressing mode

Finally, we allow an **immediate constant addressing mode**. The constant is prefixed by `#`. The instruction `LD R1, #100` loads the integer 100 into register R1, and `ADD R1, R1, #100` adds the integer 100 into register R1.


翻译: 最后，硬件还支持**立即数寻址模式**，立即数前面添加前缀 `#` 进行标记。
指令 `LD R1, #100` 的作用是将常数100载入寄存器 R1；
`ADD R1, R1, #100` 代表把数值100加到寄存器 R1 的原有数值之上。



### Comments

Comments at the end of instructions are preceded by `//`.

### Example 8.2

**Example 8.2**: The three‑address statement $\boldsymbol{x = y - z}$ can be implemented by the machine instructions:
