# Expert RednaxelaFX

zhihu [RednaxelaFX](https://www.zhihu.com/people/rednaxelafx)

## zhihu [学习编程语言与编译优化的一个书单](https://zhuanlan.zhihu.com/p/20130808)



[aamine](https://github.com/aamine)/**[cbc](https://github.com/aamine/cbc)**



## zhihu [如何理解v8的sea of nodes IR设计，能否推荐一些paper阅读？](https://www.zhihu.com/question/290982869/answer/474629999)



## zhihu [编译器具体实现中比较巧妙的思想有哪些？](https://www.zhihu.com/question/27943883/answer/39035471)





### [RednaxelaFX的回答 - 知乎](https://www.zhihu.com/question/27943883/answer/39035471) 



#### LLVM

说到编译器实现，不得不落个俗套说说 [LLVM](https://link.zhihu.com/?target=http%3A//llvm.org/) 编译器套件。不用介绍LLVM是啥了，感觉是“地球人都知道”系列。

1、一套IR，三种表现形式：

运行时表现形式（ [llvm/IR](https://link.zhihu.com/?target=http%3A//llvm.org/docs/ProgrammersManual.html%23the-core-llvm-class-hierarchy-reference)，内存中）、序列化表现形式（[bitcode](https://link.zhihu.com/?target=http%3A//llvm.org/docs/BitCodeFormat.html)，用于存储）、文本表现形式（[“LLVM汇编”](https://link.zhihu.com/?target=http%3A//llvm.org/docs/LangRef.html)，便于人阅读和编辑）。三种形式间可以无损变换是LLVM非常非常强大的实现特点之一。

实际使用时能否真的达到无损变换很大程度上取决于要实现的语言有多少东西无法用LLVM IR表达。

例如说如果有语言实现基于LLVM来实现[JIT编译器](https://www.zhihu.com/search?q=JIT编译器&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})，并且想把一个运行时的[对象指针](https://www.zhihu.com/search?q=对象指针&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})当作常量嵌入生成的代码里，它可以把这个常量构造成LLVM IR，但如果把这个常量序列化到bitcode或生成文本形式，等“下一次编译”再读出来用的话，那个[常量指针](https://www.zhihu.com/search?q=常量指针&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})可能已经不对了。这跟生成PIC（position-independent code）的问题类似，但LLVM没办法帮语言解决这种问题。

也有可能有些语言实现偷懒，有些嵌入LLVM IR的[metadata](https://www.zhihu.com/search?q=metadata&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})无法无损转换为文本形式，这也不能怪LLVM IR不好，但确实是使用中要头疼的问题…

这种一套IR三种表现形式的设计非常实用，一些新的语言实现项目受其影响也采用了类似的设计。

例如 [Australian National University](https://link.zhihu.com/?target=http%3A//www.anu.edu.au/) 主导的 [MicroVM](https://link.zhihu.com/?target=http%3A//microvm.github.io/) （μVM）项目，其 [μVM IR](https://link.zhihu.com/?target=https%3A//github.com/microvm/microvm-spec/wiki/uvm-ir) 跟LLVM IR非常相似，也自然采纳了“三种表现形式”的做法。μVM的规范里只定义了两种标准格式：文本格式与序列化格式；至于运行时形式可以由各个μVM实现自行定义，只要能兼容两种标准格式即可。

2、对IR的变换，组织为相对独立的 [Pass](https://link.zhihu.com/?target=http%3A//llvm.org/docs/WritingAnLLVMPass.html) ，并用 [PassManager](https://link.zhihu.com/?target=http%3A//llvm.org/docs/doxygen/html/classllvm_1_1PassManager.html) 来管理起来。

相对独立的Pass设计用 [opt](https://link.zhihu.com/?target=http%3A//llvm.org/docs/CommandGuide/opt.html) 命令单独执行一个Pass。

未完待续…

3、[bugpoint](https://link.zhihu.com/?target=http%3A//llvm.org/docs/Bugpoint.html)

抓虫小能手…

未完待续…

#### HotSpot Server Compiler (HotSpot C2)

HotSpot VM是Oracle/Sun JDK以及OpenJDK里的JVM实现。C2是HotSpot Server VM里的JIT编译器，是一个“较为优化”的实现。

C2的简单入门介绍可以参考我以前写的个回答：

[回复：[HotSpot VM\] 想研究HotSpot C2编译器编译过程，请教如何入手？](https://link.zhihu.com/?target=http%3A//hllvm.group.iteye.com/group/topic/39493%23post-258162)

关键词：Sea-of-nodes形式的Program Dependence Graph（PDG）。

未完待续…

采用类似的sea-of-nodes PDG作为IR的编译器还有：

[libFirm](https://link.zhihu.com/?target=http%3A//pp.ipd.kit.edu/firm/) 它有个online playground，想了解它的话很容易上手玩，可以看到代码对应的IR图的样子：

[Firm Online Compiler](https://link.zhihu.com/?target=http%3A//kreacher.isla-de-muerta.de/~matze/online_compiler/)[Graal](https://link.zhihu.com/?target=http%3A//openjdk.java.net/projects/graal/) Graal IR论文 

[Graal IR: An Extensible Declarative Intermediate Representation](https://link.zhihu.com/?target=http%3A//ssw.jku.at/General/Staff/GD/APPLC-2013-paper_12.pdf) [CACAO VM](https://link.zhihu.com/?target=http%3A//www.cacaojvm.org/) 的 [Second-stage Compiler](https://link.zhihu.com/?target=http%3A//c1.complang.tuwien.ac.at%3A8010/compiler2/doxygen/Compiler_8hpp.html)

[V8 JavaScript Engine](https://link.zhihu.com/?target=https%3A//code.google.com/p/v8/) 的 [TurboFan](https://link.zhihu.com/?target=https%3A//chromium.googlesource.com/v8/v8.git/%2B/master/src/compiler/)

TurboFan是V8新的优化编译器，目前还在早期[开发阶段](https://www.zhihu.com/search?q=开发阶段&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})。如果把V8当前的optimizing compiler跟HotSpot C1类比，那么TurboFan就跟HotSpot C2在一个级别。

[ART](https://link.zhihu.com/?target=http%3A//source.android.com/devices/tech/dalvik/) 的 [Sea IR](https://link.zhihu.com/?target=https%3A//android.googlesource.com/platform/art/%2B/407d77f344cfbdbbfb50531c5f0766bc0892e2fe/compiler/sea_ir/) （在platform/art的master上已删除）。Sea IR是ART里基于LLVM的编译器后端的其中一个；主要的基于LLVM的后端是另外一个，叫做Portable，也已经被废弃了；在这俩之前其实还有一个，被Portable替代了。

ActionScript 3/AVM2的优化器（未发布项目）。Adobe做过一个实验性的AS3优化器，

#### JamVM

[JamVM](https://link.zhihu.com/?target=http%3A//jamvm.sourceforge.net/) 是一个小巧的JVM实现，麻雀虽小五脏具全。它既可以在桌面、服务器场景中用搭配 [GNU Classpath](https://link.zhihu.com/?target=http%3A//www.gnu.org/software/classpath/) 或 [OpenJDK](https://link.zhihu.com/?target=http%3A//openjdk.java.net/) 的类库用于Java SE的实现，也可以在嵌入式场景中用于Java ME的实现。

JamVM以C语言实现，在某些配置下使用了GCC的语法扩展（例如 [computed goto](https://link.zhihu.com/?target=https%3A//gcc.gnu.org/onlinedocs/gcc/Labels-as-Values.html) ）。

关键词：Inline-threaded Interpreter

题主问的不是编译器的实现么，为啥这里会冒出[解释器](https://www.zhihu.com/search?q=解释器&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})？

因为“inline-threaded interpreter”还有另一个名字，“code-copying JIT”，或者叫“template-based JIT”；每种叫法的侧重点、出发点不同，但所指的东西其实是一样的。

一个字节码解释器可以组织为每个opcode有一个对应的[执行程序](https://www.zhihu.com/search?q=执行程序&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})（handler）。既然opcode到handler的对应关系是固定的，而我们又可以知道一个要执行的方法里的所有字节码，那么把每条字节码指令对应的handler代码拷贝出来粘合在一起，不就做成一个编译器了么？

这种做法的好处是：

- 可以作为解释器性能升级的一个简单路径，写解释器的代码而得到初级编译器的性能。事实上JamVM的解释器可以配置为多种实现方式：switch-threading、indirect-threading、direct-threading、inline-threading，它们的差别仅在于对opcode的dispatch方式不同；所有实现方式都共享同一份handler代码。

这种做法的缺点是：

- 这样写得到的“编译器”无论从代码组织还是程序思路都还是解释器的那套，从编译器的角度看很别扭。它最终实现出来效果跟从编译器角度出发的template-based JIT一样，但我觉得后者的思路更直观，代码也通常更清晰一些。
- 这种做法仍然无法跨越字节码边界做任何优化，因为每个opcode对应一个单独的handler，而这种做法的[代码生成](https://www.zhihu.com/search?q=代码生成&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})仅仅是把handler拷贝到一起而已。
- 要在它的基础之上进一步提高性能可以直接对字节码序列做些简单模式匹配，以便跨越字节码边界做优化。但这样做通常是自讨苦吃，工程上很难持续下去。

贴一小块代码给大家感受一下“一套解释器，多种实现”是什么样子的。熟悉C语言的同学肯定猜到了，这意味着一大堆奇怪的宏…

src/interp/engine/interp.c

```c
uintptr_t *executeJava() {

    /* Definitions specific to the particular
       interpreter variant */
    INTERPRETER_DEFINITIONS

   /* Caching is supported in all variants and
      may be enabled or disabled */
#ifdef USE_CACHE
    union {
        struct {
            uintptr_t v1;
            uintptr_t v2;
        } i;
        int64_t l;
    } cache;
#endif

    /* Variable definitions holding the interpreter
       state.  These are common to all interpreter
       variants */
    uintptr_t *arg1;
    register CodePntr pc;
    ExecEnv *ee = getExecEnv();
    Frame *frame = ee->last_frame;
    register uintptr_t *lvars = frame->lvars;
    register uintptr_t *ostack = frame->ostack;

    Object *this = (Object*)lvars[0];
    MethodBlock *new_mb, *mb = frame->mb;
    ConstantPool *cp = &(CLASS_CB(mb->class)->constant_pool);

    /* Initialise pc to the start of the method.  If it
       hasn't been executed before it may need preparing */
    PREPARE_MB(mb);
    pc = (CodePntr)mb->code;

    /* The initial dispatch code - this is specific to
       the interpreter variant */
    INTERPRETER_PROLOGUE

    /* Definitions of the opcode handlers */

#define MULTI_LEVEL_OPCODES(level)                         \
    DEF_OPC(OPC_ICONST_M1, level,                          \
        PUSH_##level(-1, 1);                               \
    )                                                      \

    /* ... */
```

这是解释器核心的共享部分。

然后来看switch-threading版的一些[宏定义](https://www.zhihu.com/search?q=宏定义&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})：

src/interp/engine/interp-indirect.h

```c
#define INTERPRETER_DEFINITIONS                            \
    /* none */

#define DISPATCH_PROLOGUE                                  \
    while(TRUE) {                                          \
        switch(*pc) {                                      \
            default:

#define label(x, y, z)                          \
    case x:

#define DISPATCH(level, ins_len)                \
{                                               \
    pc += ins_len;                              \
    break;                                      \
}
```

这样编译出来的解释器就是大家耳熟能详的 while (TRUE) { switch { ... } }形式。

然后看看indirect-threading版：

src/interp/engine/interp-indirect.h

```c
#define INTERPRETER_DEFINITIONS                            \
    DEFINE_HANDLER_TABLES

#define DISPATCH_PROLOGUE                                  \
    DISPATCH_FIRST                                         \
unused:

#if (__GNUC__ == 2) && (__GNUC_MINOR__ <= 95)
#define label(x, y, z)                          \
opc##x##_##y##_##z##:
#else
#define label(x, y, z)                          \
opc##x##_##y##_##z:
#endif

#define DISPATCH(level, ins_len)                \
{                                               \
    pc += ins_len;                              \
    goto *handlers_##level##_ENTRY[*pc];        \
}
```

这样编译出来的解释器就是使用了GCC的computed goto语法扩展的indirect-threading（或者叫token-threading）。

然后是这一节的关键字，inline-threading…代码贴出来太麻烦，大家自己去看吧：

src/interp/engine/interp-inlining.h

类似的做法在更早的解释器就已经有所应用。例子之一是

[SableVM](https://link.zhihu.com/?target=http%3A//www.sablevm.org/)

。

描述SableVM做法的论文：

[Effective inline-threaded interpretation of Java bytecode using preparation sequences](https://link.zhihu.com/?target=http%3A//citeseerx.ist.psu.edu/viewdoc/summary%3Fdoi%3D10.1.1.90.8603)

#### SquirrelFish Extreme (SFX)

SFX是Apple JavaScriptCore的一个比较老（2008年）的实现，参考 

[Introducing SquirrelFish Extreme](https://link.zhihu.com/?target=https%3A//www.webkit.org/blog/214/introducing-squirrelfish-extreme/)

；宣传中的代号是Nitro。后来新的JavaScriptCore有了更正常、传统一些的编译器，但这里我想写的是链接中描述的老的“Context-threaded JIT”。

[Context Threading: A flexible and efficient dispatch technique for virtual machine interpreters](https://link.zhihu.com/?target=http%3A//www.cs.toronto.edu/syslab/pubs/demkea_context.ps)



这是比inline-threading略弱的、介于解释器与编译器之间的一种实现方式。

未完待续…

#### Managed JScript

[Managed JScript](https://link.zhihu.com/?target=http%3A//blogs.msdn.com/b/deepak/archive/2007/05/02/managed-jscript-is-availaible.aspx)

是微软基于

[Dynamic Language Runtime](https://link.zhihu.com/?target=http%3A//dlr.codeplex.com/)

（DLR）实现的JavaScript引擎。当初目标是完全兼容ECMAScript 3标准。做到一半项目被坎，所以Managed JScript从来没有正式发布过。最后发布的版本是在Silverlight Dynamic Language SDK 0.4.0带的那个。

关于它的背景，请参考链接帖：

[[链接帖\] 各JavaScript引擎的简介，及相关资料/博客收集帖讨论第2页](https://link.zhihu.com/?target=http%3A//hllvm.group.iteye.com/group/topic/37596%3Fpage%3D2%23post-243750)

要拿这种已死的老项目出来举栗子是因为它的[parser](https://www.zhihu.com/search?q=parser&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})挺特别：使用纯[运算符优先级](https://www.zhihu.com/search?q=运算符优先级&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})（operator precedence）形式的自顶向下parser。

[Top Down Operator Precedence](https://link.zhihu.com/?target=http%3A//javascript.crockford.com/tdop/tdop.html)

未完待续…

TODO

Dynamic Superinstruction

compiler benchmark cheating LINPACK DONGARRA FORTRAN



## zhihu [如何评价只有 LLVM 10% 代码的 QBE？](https://www.zhihu.com/question/43956056/answer/97177805)