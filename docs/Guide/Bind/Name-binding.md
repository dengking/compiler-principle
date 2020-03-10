# [Name-binding](https://en.wikipedia.org/wiki/Name_binding)

For bound variables in mathematics, see [free variables and bound variables](https://en.wikipedia.org/wiki/Free_variables_and_bound_variables).

In [programming languages](https://en.wikipedia.org/wiki/Programming_language), **name binding** is the association of entities (data and/or code) with [identifiers](https://en.wikipedia.org/wiki/Identifier).[[1\]](https://en.wikipedia.org/wiki/Name_binding#cite_note-tkac08-1) An identifier bound to an object is said to [reference](https://en.wikipedia.org/wiki/Reference_(computer_science)) that object(此处的object就是上一句提到的entity). [Machine languages](https://en.wikipedia.org/wiki/Machine_language)(可以直接有CPU运行的语言) have no built-in notion of identifiers(机器语言没有内置的identifier的概念), but name-object bindings(name和object的binding) as a service and notation for the programmer is implemented by programming languages(binding是由programming languages来实现的). **Binding** is intimately(紧密地) connected with [scoping](https://en.wikipedia.org/wiki/Scoping), as scope determines which names bind to which objects – at which locations in the program code ([lexically](https://en.wikipedia.org/wiki/Scope_(computer_science)#Lexical_scoping)) and in which one of the possible execution paths ([temporally](https://en.wikipedia.org/wiki/Scope_(computer_science)#Dynamic_scoping))(binding与scope密切相关，因为scope 确定哪些name绑定到哪些object - 程序代码中的哪些位置（词法）以及哪个可能的执行路径（临时）).

Use of an identifier `id` in a context that establishes a binding for `id` is called a **binding (or defining) occurrence**(绑定事件或定义事件. In all other occurrences (e.g., in expressions, assignments, and subprogram calls), an identifier stands for what it is bound to; such occurrences are called **applied occurrences**(在为id建立绑定的上下文中使用标识符id称为绑定（或定义）事件。 在所有其他事件中（例如，在表达式，赋值和子程序调用中），标识符代表它所绑定的内容; 这种事件称为应用事件).

思考：name binding和scope的关系

总结：显然name-binding和by reference是密切相关的。

## Binding time

- *Static binding* (or *early binding*) is **name binding** performed before the program is run [[2\]](https://en.wikipedia.org/wiki/Name_binding#cite_note-ieee24765:2010(E)-2).
- *Dynamic binding* (or *late binding* or *virtual binding*) is **name binding** performed as the program is running [[2\]](https://en.wikipedia.org/wiki/Name_binding#cite_note-ieee24765:2010(E)-2).

An example of a **static binding** is a direct [C](https://en.wikipedia.org/wiki/C_(programming_language)) function call: the function referenced by the identifier cannot change at runtime.

But an example of **dynamic binding** is [dynamic dispatch](https://en.wikipedia.org/wiki/Dynamic_dispatch), as in a [C++](https://en.wikipedia.org/wiki/C%2B%2B) virtual method call. Since the specific type of a [polymorphic](https://en.wikipedia.org/wiki/Polymorphism_(computer_science)) object is not known before runtime (in general), the executed function is dynamically bound. Take, for example, the following [Java](https://en.wikipedia.org/wiki/Java_(programming_language)) code:

```java
 public void foo(java.util.List<String> list) {
     list.add("bar");
 }
```

`List` is an [interface](https://en.wikipedia.org/wiki/Interface_(computing)), so `list` must refer to a [subtype](https://en.wikipedia.org/wiki/Subtype) of it. Is it a reference to a `LinkedList`, an `ArrayList`, or some other [subtype](https://en.wikipedia.org/wiki/Subtype) of `List`? The actual method referenced by `add` is not known until runtime. In C, such instance of **dynamic binding** may be a call to a function pointed by a variable or expression of a **function pointer type** whose value is unknown until it actually gets evaluated at run-time.

总结：上面这段话还描述了C语言中实现**dynamic binding**的方式。

## Rebinding and mutation

**Rebinding** should not be confused with **mutation**(突变，改变).

- *Rebinding* is a change to the *referencing* identifier.
- *Mutation* is a change to the *referenced* entity.

Consider the following [Java](https://en.wikipedia.org/wiki/Java_(programming_language)) code:

```java
 LinkedList<String> list;
 list = new LinkedList<String>();
 list.add("foo");
 list = null;
```

The identifier `list` initially references nothing (it is [uninitialized](https://en.wikipedia.org/wiki/Uninitialized_variable)); it is then rebound to reference an object (a linked list of strings). The linked list referenced by `list` is then mutated, adding a string to the list. Lastly, `list` is rebound to `null`.

## Late static

**Late static binding** is a variant of binding somewhere between static and dynamic binding. Consider the following [PHP](https://en.wikipedia.org/wiki/PHP) example:

```PHP
class A {
    static $word = "hello";
    static function hello() { print self::$word; }
}

class B extends A {
    static $word = "bye";
}

B::hello();
```

In this example, the `PHP` interpreter binds the keyword `self` inside `A::hello()` to class `A`, and so the call to `B::hello()` produces the string "hello". If the semantics of `self::$word` had been based on late static binding, then the result would have been "bye".

Beginning with PHP version 5.3, late static binding is supported.[[3\]](https://en.wikipedia.org/wiki/Name_binding#cite_note-3) Specifically, if `self::$word` in the above were changed to `static::$word` as shown in the following block, where the keyword `static` would only be bound at runtime, then the result of the call to `B::hello()` would be "bye":

```c++
class A {
    static $word = "hello";
    static function hello() { print static::$word; }
}

class B extends A {
    static $word = "bye";
}

B::hello();
```

