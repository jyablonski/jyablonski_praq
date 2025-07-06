# Abstract Syntax Tree

An Abstract Syntax Tree (AST) is a tree representation of the structured meaning of source code. Instead of treating code as raw text, programming languages first parse the code into an AST to make it easier to analyze, transform, and execute.

Each node in the tree represents a construct in the language — such as a variable assignment, function definition, loop, or expression — and the tree’s shape reflects how these constructs are nested and related.

The tree is called “abstract” because it omits superficial details like parentheses, whitespace, and comments, focusing instead on the semantic structure of the code.

Python provides a built-in module called `ast` to parse Python code into an AST, and also to inspect or modify it.

## Why is AST useful?

* Tools can analyze, transform, or generate Python code by working with the AST rather than raw text.
* It enables static analysis (like linters, type checkers), code formatting, refactoring tools, or code instrumentation.
* Also used in compilers and interpreters internally to understand and execute your code.
* You can write Python code that modifies other Python code safely by manipulating the AST.

## When would you use AST?

* Writing linters or static analyzers: To check code style or detect errors without running the code.
* Code formatters: Like `black` or `ruff`, that parse code and rewrite it cleanly.
* Code transformation: Auto-generate code or modify code automatically (e.g., adding logging, instrumentation).
* Code introspection tools: Analyze what a function does or gather metadata.
* Education and visualization: Understand how Python parses and executes code.

There are several advantages to parsing code w/ AST rather than parsing raw Python code:

- More reliable than text parsing because AST understands the syntax rules and grammar of Python
- More performant because code is broken down into nodes that tools can efficiently traverse the parts they're interested in
- It's safer to use the AST than rely on brittle text patterns to understand the meaning of the code and distinguish from actual function calls vs comments etc

## AST Example

``` py
Module(
    body=[
        FunctionDef(
            name='greet',
            args=arguments(
                posonlyargs=[],
                args=[
                    arg(arg='name')],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]),
            body=[
                Expr(
                    value=Call(
                        func=Name(id='print', ctx=Load()),
                        args=[
                            BinOp(
                                left=BinOp(
                                    left=BinOp(
                                        left=Constant(value='Hello, '),
                                        op=Add(),
                                        right=Name(id='name', ctx=Load())),
                                    op=Add(),
                                    right=Constant(value='!')),
                                op=Add(),
                                right=Constant(value='boobs'))],
                        keywords=[]))],
            decorator_list=[],
            type_params=[]),
        Expr(
            value=Call(
                func=Name(id='greet', ctx=Load()),
                args=[
                    Constant(value='Alice')],
                keywords=[]))],
    type_ignores=[])

```

AST Nodes correspond closely to Python syntax constructs

* Each node type in the AST represents a specific syntax element:

  * `Module` for the whole file/module
  * `FunctionDef` for function definitions
  * `ClassDef` for classes
  * `Assign` for assignments
  * `Expr` for expressions
  * `Call` for function calls
  * `If`, `For`, `While` for control flow statements
  * `BinOp` for binary operations (`+`, `-`, `*`, `/`), etc.

* The full list of node types is in the [official Python docs](https://docs.python.org/3/library/ast.html#abstract-grammar).

Some nodes (like Name) have a ctx attribute specifying the context:

- Load means the variable is read
- Store means the variable is written/assigned
- Del means the variable is deleted
