zhihu [编译器具体实现中比较巧妙的思想有哪些？](https://www.zhihu.com/question/27943883/answer/39035471) # [RednaxelaFX的回答 - 知乎](https://www.zhihu.com/question/27943883/answer/39035471)
> 
> 说到编译器实现，不得不落个俗套说说 [LLVM](https://link.zhihu.com/?target=http%3A//llvm.org/) 编译器套件。不用介绍LLVM是啥了，感觉是“地球人都知道”系列。
> 
> 1、一套IR，三种表现形式：
> 
> 运行时表现形式（ [llvm/IR](https://link.zhihu.com/?target=http%3A//llvm.org/docs/ProgrammersManual.html%23the-core-llvm-class-hierarchy-reference)，内存中）、序列化表现形式（[bitcode](https://link.zhihu.com/?target=http%3A//llvm.org/docs/BitCodeFormat.html)，用于存储）、文本表现形式（[“LLVM汇编”](https://link.zhihu.com/?target=http%3A//llvm.org/docs/LangRef.html)，便于人阅读和编辑）。三种形式间可以无损变换是LLVM非常非常强大的实现特点之一。
> 
> 实际使用时能否真的达到无损变换很大程度上取决于要实现的语言有多少东西无法用LLVM IR表达。
> 
> 例如说如果有语言实现基于LLVM来实现[JIT编译器](https://www.zhihu.com/search?q=JIT编译器&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})，并且想把一个运行时的[对象指针](https://www.zhihu.com/search?q=对象指针&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})当作常量嵌入生成的代码里，它可以把这个常量构造成LLVM IR，但如果把这个常量序列化到bitcode或生成文本形式，等“下一次编译”再读出来用的话，那个[常量指针](https://www.zhihu.com/search?q=常量指针&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})可能已经不对了。这跟生成PIC（position-independent code）的问题类似，但LLVM没办法帮语言解决这种问题。
> 
> 也有可能有些语言实现偷懒，有些嵌入LLVM IR的[metadata](https://www.zhihu.com/search?q=metadata&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"answer"%2C"sourceId"%3A39035471})无法无损转换为文本形式，这也不能怪LLVM IR不好，但确实是使用中要头疼的问题…
> 
> 这种一套IR三种表现形式的设计非常实用，一些新的语言实现项目受其影响也采用了类似的设计。
> 
> 例如 [Australian National University](https://link.zhihu.com/?target=http%3A//www.anu.edu.au/) 主导的 [MicroVM](https://link.zhihu.com/?target=http%3A//microvm.github.io/) （μVM）项目，其 [μVM IR](https://link.zhihu.com/?target=https%3A//github.com/microvm/microvm-spec/wiki/uvm-ir) 跟LLVM IR非常相似，也自然采纳了“三种表现形式”的做法。μVM的规范里只定义了两种标准格式：文本格式与序列化格式；至于运行时形式可以由各个μVM实现自行定义，只要能兼容两种标准格式即可。
> 
> 2、对IR的变换，组织为相对独立的 [Pass](https://link.zhihu.com/?target=http%3A//llvm.org/docs/WritingAnLLVMPass.html) ，并用 [PassManager](https://link.zhihu.com/?target=http%3A//llvm.org/docs/doxygen/html/classllvm_1_1PassManager.html) 来管理起来。
> 
> 相对独立的Pass设计用 [opt](https://link.zhihu.com/?target=http%3A//llvm.org/docs/CommandGuide/opt.html) 命令单独执行一个Pass。
> 
> 未完待续…
> 
> 3、[bugpoint](https://link.zhihu.com/?target=http%3A//llvm.org/docs/Bugpoint.html)
> 
> 抓虫小能手…
> 
> 未完待续…