# 树

## 0. 与链表的核心区别

链表的定义中，自身**只出现一次**，属于线性递归；树的定义中，自身**出现两次或更多次**，属于树形递归。

```EBNF
list → ε | value list              （1 个自身引用 → 链表）
tree → ε | tree value tree         （2 个自身引用 → 二叉树）
```

可以这样理解：**每个节点只有一个"后继"就是链表，有多个"后继"就是树。** 链表是树的特例，即每个节点只有一个孩子的树。

## 1. 二叉树

### 数学定义

1. 空树是二叉树（基础情形）；
2. 如果 L 和 R 是二叉树，v 是一个值，那么 `Node(L, v, R)` 也是二叉树（递归情形）；
3. 除此之外没有别的二叉树。

### 构造器形式

```
Tree → Empty | Node(Tree, value, Tree)
```

### 文法形式（树的文本表示）

为了让文法能生成字符串，需要给树一种书写方式。这里用 `.` 表示空树，用括号包住一个节点：

```ebnf
tree → '.' | '(' tree NUMBER tree ')'
```

例如：

```
((. 1 .) 2 (. 3 .))

        2
       / \
      1   3
```

这条产生式中 `tree` 在右侧出现了两次，既不是左递归，也不是右递归，而是**两侧都递归**，括号起到界定嵌套的作用。

### Haskell

```haskell
data Tree a = Empty
            | Node (Tree a) a (Tree a)
```

### C

```c
struct Tree {
    struct Tree *left;    // 第一个自身引用
    int value;
    struct Tree *right;   // 第二个自身引用
};
// NULL 表示空树
```

可以与链表对照：链表的 `struct Node` 只有一个 `next` 指针，这里有两个。

### 常见变体

| 变体 | 定义 | 说明 |
|---|---|---|
| 节点存值 | `Tree → Empty \| Node(Tree, v, Tree)` | 最常见，如 BST |
| 叶子存值 | `Tree → Leaf(v) \| Node(Tree, Tree)` | 如哈夫曼树、表达式树 |
| 非空二叉树 | `Tree → Leaf(v) \| Node(Tree, v, Tree)` | 没有空树 |

二叉搜索树（BST）的**结构**与二叉树完全相同，只是多了一个约束：左子树的值都小于 v，右子树的值都大于 v。这类"值之间的大小关系"无法用上下文无关文法表达，属于定义之外的不变式。

## 2. 多叉树（rose tree）：树和列表的相互递归

如果每个节点可以有任意多个孩子，就要借助"树的列表"（森林）来定义：

```
tree   → Node(value, forest)
forest → Nil | Cons(tree, forest)
```

可以看出 `forest` 就是一个**普通链表**，只是元素是树。这是第一条回答中提到的**间接递归**：`tree → forest → tree`。

### 文法形式

```ebnf
tree   → '(' VALUE forest ')'
forest → tree forest | ε          （右递归，等价于 { tree }）
```

例如 `(A (B) (C (D) (E)))` 表示：

```
      A
     / \
    B   C
       / \
      D   E
```

这其实就是 Lisp 的 S-表达式，也是 HTML/XML 的结构：一个元素包含任意多个子元素。

### Haskell

```haskell
data Rose a = Rose a [Rose a]     -- [Rose a] 就是 forest
```

### C（孩子-兄弟表示法）

```c
struct Node {
    int value;
    struct Node *first_child;    // 指向 forest 的第一个元素
    struct Node *next_sibling;   // forest 本身是链表
};
```

这种表示法说明了一点：**任何多叉树都可以编码成二叉树**，两个指针分别对应"进入下一层"和"同层的下一个"。

## 3. 表达式树：回到 `expr` 文法

`1 + 2 * 3` 的抽象语法树（AST）定义如下：

```haskell
data Expr = Num Int
          | Var String
          | Add Expr Expr      -- 两个自身引用
          | Mul Expr Expr      -- 两个自身引用
```

如果把它直接写成文法：

```ebnf
expr → expr '+' expr | expr '*' expr | NUMBER | IDENT | '(' expr ')'
```

这个文法描述的语言与原文法相同，但它是**有歧义**的。原因正是树形递归：`expr '+' expr` 的两侧都能继续展开，所以同一个字符串可以对应多棵树。

```
1 + 2 * 3

     +              *
    / \            / \
   1   *          +   3
      / \        / \
     2   3      1   2
   （正确）      （错误）
```

### 原文法做了什么

原文法 `expr → expr '+' term` 把右边的 `expr` 换成了更低一层的 `term`：

| 文法 | 递归形式 | 生成的结构 | 是否有歧义 |
|---|---|---|---|
| `expr → expr '+' expr` | 两侧都递归 | 任意形状的二叉树 | 有 |
| `expr → expr '+' term` | 只有左侧递归 | 向左倾斜的树（snoc 列表） | 无 |

原文法**限制了树的形状**：每个 `+` 节点的右孩子只能是 term，不能再是带 `+` 的 expr，于是树只能向左延伸，形状变成了上一条回答中的 snoc 列表。再加上 expr / term / factor 的分层，`*` 必然位于 `+` 的下层，从而同时确定了优先级和结合性。

可以总结为：
- **AST 的定义是树形递归**（`Add Expr Expr`），描述运算的结构；
- **具体文法是分层的线性递归**，通过限制递归方向和层次消除歧义，保证每个字符串只解析出一棵树。

## 4. 定义的形状决定函数的形状

对递归数据结构编写函数时，函数的递归结构与定义一一对应（结构递归）：

```haskell
-- 链表：一个自身引用 → 一次递归调用
length Nil         = 0
length (Cons _ xs) = 1 + length xs

-- 二叉树：两个自身引用 → 两次递归调用
size Empty        = 0
size (Node l _ r) = size l + 1 + size r

depth Empty        = 0
depth (Node l _ r) = 1 + max (depth l) (depth r)

-- 表达式树：求值
eval (Num n)   = n
eval (Add a b) = eval a + eval b
eval (Mul a b) = eval a * eval b

-- 多叉树：对 forest 使用列表函数
sizeRose (Rose _ kids) = 1 + sum (map sizeRose kids)
```

## 5. 总结

| 结构 | 递归定义 | 自身引用次数 | 递归类型 |
|---|---|---|---|
| 链表 | `List → Nil \| Cons(v, List)` | 1 | 线性递归 |
| 二叉树 | `Tree → Empty \| Node(Tree, v, Tree)` | 2 | 树形递归 |
| 多叉树 | `Tree → Node(v, [Tree])` | 任意多 | 与列表相互递归 |
| 表达式 AST | `Expr → Num \| Add(Expr, Expr) \| …` | 2 | 树形递归 |
| `expr` 具体文法 | `expr → expr '+' term \| term` | 1 | 线性递归 + 分层 |

链表、树和文法本质上是同一件事：**基础情形加上用自身构造更大对象的规则**。自身引用的次数决定了结构的形状：一次得到链，两次或更多次得到树。