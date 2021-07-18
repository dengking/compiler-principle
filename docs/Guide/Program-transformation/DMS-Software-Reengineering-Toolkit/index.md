# DMS® Software Reengineering Toolkit™

是在阅读 [Aspect Oriented Programming in C++ - Current supported alternatives](https://stackoverflow.com/questions/4200183/aspect-oriented-programming-in-c-current-supported-alternatives) # [A](https://stackoverflow.com/a/4331966) 时，发现的:

> Aspect-oriented programming is a just a special kind of program transformation ("*find places that match this condition ('pointcut') and do this to the code at that place*"). So, if you have a program transformation tool, you can emulate AOP pretty easily. To do transformation on C++ you need a strong C++ front end and as well as ability to transform and regenerate code. OpenC++ was a project to do C++ transformations, where the transformations are coded purely as procedural AST-walks with procedural AST modifications. A particular issue had to do with which dialect of C++ was handled by OpenC++; in particular, I'm not sure OpenC++ handled templates or full common dialects (GCC, MS) of C+; however I have no direct experience with it, just a keen aficionado of such tools.
>
> Our [DMS Software Reengineering Toolkit](http://www.semanticdesigns.com/Products/DMS/DMSToolkit.html) is a general purpose program transformation parameterized by language definitions. It has [robust definitions for GCC and MS dialects of C++](http://www.semanticdesigns.com/Products/FrontEnds/CppFrontEnd.html). You can implement program transformations procedurally as OpenC++ does, or more conveniently you can write source-to-source pattern-directed transformations (or more usually, mix these to achieve complex effects). DMS has been used to carry out massive restructuring of large scale C++ codes (see [Case study: Re-engineering C++ component models via automatic program transformation ](http://www.sciencedirect.com/science?_ob=ArticleURL&_udi=B6V0B-4MJS01P-1&_user=10&_coverDate=03%2F31%2F2007&_rdoc=1&_fmt=high&_orig=search&_origin=search&_sort=d&_docanchor=&view=c&_searchStrId=1565023185&_rerunOrigin=google&_acct=C000050221&_version=1&_urlVersion=0&_userid=10&md5=0c068720962ea8f513f8e69c6b41ae42&searchtype=a)). DMS is actively maintained, but it is commercial.



## semanticdesigns [DMS® Software Reengineering Toolkit™](http://www.semanticdesigns.com/Products/DMS/DMSToolkit.html)

## wikipedia [DMS Software Reengineering Toolkit](https://en.wikipedia.org/wiki/DMS_Software_Reengineering_Toolkit)

