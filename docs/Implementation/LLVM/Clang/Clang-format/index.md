# Clang format

[ClangFormat](https://clang.llvm.org/docs/ClangFormat.html)

[Clang-Format Style Options](https://clang.llvm.org/docs/ClangFormatStyleOptions.html)

```yaml
Language: Cpp
BasedOnStyle: Google
ColumnLimit: 120

# 自动识别代码中的指针对齐方式，如果希望强制统一，则可以改为 false
DerivePointerAlignment: true

# 默认对齐到类型名
PointerAlignment: Left

# Only sort headers in each include block
SortIncludes: true
IncludeBlocks: Preserve

# 让 #if/#else/#endif 宏中的内容保持缩进，比如：
#   #if defined(WIN)
#   #  include <windows.h>
#   #else
#   #  include <curl.h>
#   #endif
IndentPPDirectives: AfterHash

# 解决 Issue 148: 不特殊看待 foreach 宏
ForEachMacros: [ '' ]

# 行注释 "//" 前增加两个空格
SpacesBeforeTrailingComments: 2

# When true, access modifiers get their own indentation level. As a consequence, record members are always indented 2 levels below the record, regardless of the access modifier presence. Value of the AccessModifierOffset is ignored.
IndentAccessModifiers: true
# Indent access specifiers by one space
AccessModifierOffset: 1
```

