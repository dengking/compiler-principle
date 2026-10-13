# Bril 的一个例子

Bril(Big Red Intermediate Language)是 Cornell CS 6120 用的教学 IR,作者是 Adrian Sampson。它的设计目标很明确:**简单到能让学生在一周内从零写出一整套工具**,同时保留真实 IR 的全部结构要素(基本块、终结指令、SSA、类型)。

几个关键设计决定:

- **规范表示是 JSON**,不是文本。文本格式只是给人看的便利层,由 `bril2json` / `bril2txt` 双向转换。
- **核心语言故意不是 SSA**。变量可以重复赋值。Sampson 的说法是"我想让学生在被 SSA 救之前先体会到非 SSA 的痛苦"。
- 指令分类:
  - **值操作**(有 `dest` + `type`)
  - **副作用操作**(无 `dest`)
  - `const`

---

## 例 1:迭代版阶乘(文本格式)

存为 `fact.bril`:

```
@main {
  n: int = const 6;
  r: int = call @fact n;
  print r;
}

# 迭代计算 n!,刻意写成非 SSA 形式
@fact(n: int): int {
  one: int = const 1;
  acc: int = const 1;
  i: int = const 1;
  jmp .test;

.test:
  done: bool = gt i n;
  br done .done .body;

.body:
  acc: int = mul acc i;     # acc 被重新赋值 —— 核心 Bril 允许
  i: int = add i one;       # i 被重新赋值
  jmp .test;

.done:
  ret acc;
}
```

跑一遍:

```bash
$ bril2json < fact.bril | brili
720
```

语法要点:

| 语法                                  | 含义                  |
| ----------------------------------- | ------------------- |
| `@name(arg: type): rettype { ... }` | 函数定义;`@` 是函数的 sigil |
| `.label:`                           | 基本块标签(带点)           |
| `x: int = add a b;`                 | 值操作,产生新值绑定到 `x`     |
| `print r;`                          | 副作用操作,无 `dest`      |
| `br cond .a .b;`                    | 二路分支,条件必须是 `bool`   |
| `jmp .a;`                           | 无条件跳转               |
| `ret x;` / `ret;`                   | 返回(有/无返回值)          |
| `x: int = call @f a b;`             | 函数调用                |

注意这里 `acc` 和 `i` 都在循环体里被**重新赋值**。这不是笔误——核心 Bril 就是变异的、命令式的,不是 SSA。`main` 必须存在,且**不能有返回类型**。

---

## 例 2:同一个程序的规范 JSON 形式

`bril2json` 会把上面的文本转成这个(节选 `fact`):

```json
{
  "functions": [
    {
      "name": "main",
      "instrs": [
        {"op": "const", "dest": "n", "type": "int", "value": 6},
        {"op": "call", "dest": "r", "type": "int", "func": "fact", "args": ["n"]},
        {"op": "print", "args": ["r"]}
      ]
    },
    {
      "name": "fact",
      "args": [{"name": "n", "type": "int"}],
      "type": "int",
      "instrs": [
        {"op": "const", "dest": "one", "type": "int", "value": 1},
        {"op": "const", "dest": "acc", "type": "int", "value": 1},
        {"op": "const", "dest": "i",   "type": "int", "value": 1},
        {"op": "jmp", "labels": ["test"]},

        {"label": "test"},
        {"op": "gt", "dest": "done", "type": "bool", "args": ["i", "n"]},
        {"op": "br", "args": ["done"], "labels": ["done", "body"]},

        {"label": "body"},
        {"op": "mul", "dest": "acc", "type": "int", "args": ["acc", "i"]},
        {"op": "add", "dest": "i",   "type": "int", "args": ["i", "one"]},
        {"op": "jmp", "labels": ["test"]},

        {"label": "done"},
        {"op": "ret", "args": ["acc"]}
      ]
    }
  ]
}
```

几个值得注意的编码细节:

- **标签是独立的对象** `{"label": "test"}`,不是指令的一部分。文本格式里的 `.test` 到 JSON 就变成了不带点的 `"test"`。
- **`br` 的第一个 label 是"条件为真"的目标**,第二个是假的分支。
- **函数对象上的 `"type"` 是返回类型**;`args` 是 `{name, type}` 列表;`main` 两者都不能有返回类型。
- `call` 的函数名放在 `"func"`(单数)字段。文档的 syntax 章节笼统地写了个 `funcs` 字段列表,和实际实现不一致——这是 Bril 文档里的一处已知瑕疵。

核心类型只有 `int` 和 `bool`;`float`、`ptr<T>`(内存扩展)、`char` 等都在扩展章节里。

---

## 例 3:SSA 扩展

SSA 在 Bril 里**是一个语言扩展**,不是核心的一部分,定义在 `docs/lang/ssa.md`。它只做一件事:**给语言加一个 `phi` 操作**。

文本语法是 `phi`,把参数和标签交织着写,解析器不在乎顺序:

```
x: int = phi a .here b .there;
```

语义:取"**第二近执行过的标签**"对应的那个参数——直观上就是**当前基本块的前驱**。用它重写上面的求和循环:

```
@main {
  n: int = const 5;
  r: int = call @sum n;
  print r;
}

@sum(n: int): int {
.pre:
  zero: int = const 0;
  one: int = const 1;
  jmp .loop;

.loop:
  i: int = phi zero .pre i_next .body;
  s: int = phi zero .pre s_next .body;
  cond: bool = lt i n;
  br cond .body .exit;

.body:
  i_next: int = add i one;
  s_next: int = add s i;
  jmp .loop;

.exit:
  ret s;
}
```

输出 `10`(= 0+1+2+3+4)。JSON 形式里 phi 的入边用 `args` 和 `labels` 两个平行数组表示:

```json
{"op": "phi", "dest": "i", "type": "int",
 "args": ["zero", "i_next"], "labels": ["pre", "body"]}
```

注意 `.pre` 这个标签:因为 phi 的前驱是靠**标签**识别的,入口块如果没有标签就没法被 phi 引用——所以这里必须显式给入口块贴一个 `.pre`。

这也暴露了 Bril 这套 SSA 的别扭之处。Sampson 自己后来公开说过,把 `phi` 当作"语义上就是一条普通指令"来接入一个变异导向的 IL 是设计错误(Bril 的 SSA 需要"彻底重做",更合适的做法是 MLIR 那种**基本块参数**),而且 Bril 的多个解释器确实把 phi 当普通指令顺序执行,因而在 phi 之间存在交叉依赖时出错。他自己举的例子正是我们前面讨论过的那个 swap:

```
L1:
  x1 = phi(L0: x0, L1: y1)
  y1 = phi(L0: y0, L1: x1)
  print(x1, y1)
  goto L1
```

顺序执行这两条 phi 会覆盖 `x1`,触发 **lost copy problem**——也就是 phi 的并行语义没有被兑现。这是 Bril 作为教学 IR 的一个很好的反面教材:它让学生亲眼看到"phi 只是另一条指令"这个直觉在哪里崩掉。

---

## 小结

- Bril 的核心是 **JSON AST + 平坦指令序列**,基本块靠标签切分,终结指令是 `jmp` / `br` / `ret`。
- 核心语言 **不是 SSA**,变量可重复赋值;`id` 提供显式拷贝,`print` 是唯一的输出副作用。
- SSA 通过**扩展**引入,只增加 `phi` 一个操作;文本写作 `x: t = phi a .here b .there;`。
- 工具链是 Unix 风格的小工具拼接:`bril2json`、`bril2txt`、`brili`(解释器,读 JSON)、`turnt`(测试)。
- 例子里那两处变量重赋值是重点,不是疏漏——理解 Bril 的第一步就是认识到它**先给你看不带 SSA 的世界**。
