# Program transformation

是在阅读 [Aspect Oriented Programming in C++ - Current supported alternatives](https://stackoverflow.com/questions/4200183/aspect-oriented-programming-in-c-current-supported-alternatives) # [A](https://stackoverflow.com/a/4331966) 时，发现的:

> Aspect-oriented programming is a just a special kind of program transformation ("*find places that match this condition ('pointcut') and do this to the code at that place*"). So, if you have a program transformation tool, you can emulate AOP pretty easily. To do transformation on C++ you need a strong C++ front end and as well as ability to transform and regenerate code. OpenC++ was a project to do C++ transformations, where the transformations are coded purely as procedural AST-walks with procedural AST modifications. A particular issue had to do with which dialect of C++ was handled by OpenC++; in particular, I'm not sure OpenC++ handled templates or full common dialects (GCC, MS) of C+; however I have no direct experience with it, just a keen aficionado of such tools.

看到了这段描述，我想到了 JavaScript [Babel (transcompiler)](https://en.wikipedia.org/wiki/Babel_(transcompiler)) ，现在想想，compiler所做的其实就是 program transformation。



## semanticdesigns [Program Transformation](http://www.semanticdesigns.com/Products/DMS/ProgramTransformation.html?Home=DMSToolkit)



## TODO

1、Google Logica

**Logica代码可以编译成SQL**

参见:

