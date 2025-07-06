import ast

# Some Python source code as a string
source_code = """
def greet(name):
    print("Hello, " + name + "!" + "boobs")
greet("Alice")
"""

# Parse the source code into an AST object
tree = ast.parse(source_code)

# Print the AST in a readable format
print(ast.dump(tree, indent=4))

# Module(
#     body=[
#         FunctionDef(
#             name='greet',
#             args=arguments(
#                 posonlyargs=[],
#                 args=[
#                     arg(arg='name')],
#                 kwonlyargs=[],
#                 kw_defaults=[],
#                 defaults=[]),
#             body=[
#                 Expr(
#                     value=Call(
#                         func=Name(id='print', ctx=Load()),
#                         args=[
#                             BinOp(
#                                 left=BinOp(
#                                     left=BinOp(
#                                         left=Constant(value='Hello, '),
#                                         op=Add(),
#                                         right=Name(id='name', ctx=Load())),
#                                     op=Add(),
#                                     right=Constant(value='!')),
#                                 op=Add(),
#                                 right=Constant(value='boobs'))],
#                         keywords=[]))],
#             decorator_list=[],
#             type_params=[]),
#         Expr(
#             value=Call(
#                 func=Name(id='greet', ctx=Load()),
#                 args=[
#                     Constant(value='Alice')],
#                 keywords=[]))],
#     type_ignores=[])
