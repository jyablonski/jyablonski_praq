# Notes

## Python vs Java
[Article](https://ggbaker.ca/prog-langs/content/lang-types.html)
Main difference is Python is dynamically typed whereas Java is statically typed.
- Pros of dynamically typed are you can develop slightly faster by not having to explicitly define each variable's type when building code.
- Cons of dynamically typed are potentially more error-prone code because variable types are inferred and aren't truly known until runtime, and performance. 

All variables, data, and other information we use when developing code for applications has to get sent to memory before being operated on by the CPU.  Everything that goes into memory must have some form of a type associated with it. If you rely on the interpreter to figure that out line by line when compiling your code, that's an extra step of the process as opposed to statically typed language where the developer defines everything in advance.

This is why C & Java are "faster" than Python; for applications with extreme performance needs this is why they need to be built in C & Java.  For most applications, the performance isn't necessary which is why Python is still very popular.

If a complex operation can run in python in ~200ms or less, then what's the point of making it go even faster in C or Java if the development time takes longer?  That's the tradeoff.  Python tends to be easier to read and faster to develop solutions for, saving development hours at the cost of code performance.

Copy Pasted from this comment [Article](https://stackoverflow.com/questions/441824/java-virtual-machine-vs-python-interpreter-parlance)

```
In this post, "virtual machine" refers to process virtual machines, not to system virtual machines like Qemu or Virtualbox. A process virtual machine is simply a program which provides a general programming environment -- a program which can be programmed.

Java has an interpreter as well as a virtual machine, and Python has a virtual machine as well as an interpreter. The reason "virtual machine" is a more common term in Java and "interpreter" is a more common term in Python has a lot to do with the major difference between the two languages: static typing (Java) vs dynamic typing (Python). In this context, "type" refers to primitive data types -- types which suggest the in-memory storage size of the data. The Java virtual machine has it easy. It requires the programmer to specify the primitive data type of each variable. This provides sufficient information for Java bytecode not only to be interpreted and executed by the Java virtual machine, but even to be compiled into machine instructions. The Python virtual machine is more complex in the sense that it takes on the additional task of pausing before the execution of each operation to determine the primitive data types for each variable or data structure involved in the operation. Python frees the programmer from thinking in terms of primitive data types, and allows operations to be expressed at a higher level. The price of this freedom is performance. "Interpreter" is the preferred term for Python because it has to pause to inspect data types, and also because the comparatively concise syntax of dynamically-typed languages is a good fit for interactive interfaces. There's no technical barrier to building an interactive Java interface, but trying to write any statically-typed code interactively would be tedious, so it just isn't done that way.

In the Java world, the virtual machine steals the show because it runs programs written in a language which can actually be compiled into machine instructions, and the result is speed and resource efficiency. Java bytecode can be executed by the Java virtual machine with performance approaching that of compiled programs, relatively speaking. This is due to the presence of primitive data type information in the bytecode. The Java virtual machine puts Java in a category of its own:

portable interpreted statically-typed language

The next closest thing is LLVM, but LLVM operates at a different level:

portable interpreted assembly language

The term "bytecode" is used in both Java and Python, but not all bytecode is created equal. bytecode is just the generic term for intermediate languages used by compilers/interpreters. Even C compilers like gcc use an intermediate language (or several) to get the job done. Java bytecode contains information about primitive data types, whereas Python bytecode does not. In this respect, the Python (and Bash,Perl,Ruby, etc.) virtual machine truly is fundamentally slower than the Java virtual machine, or rather, it simply has more work to do. It is useful to consider what information is contained in different bytecode formats:

llvm: cpu registers
Java: primitive data types
Python: user-defined types
To draw a real-world analogy: LLVM works with atoms, the Java virtual machine works with molecules, and The Python virtual machine works with materials. Since everything must eventually decompose into subatomic particles (real machine operations), the Python virtual machine has the most complex task.

Intepreters/compilers of statically-typed languages just don't have the same baggage that interpreters/compilers of dynamically-typed languages have. Programmers of statically-typed languages have to take up the slack, for which the payoff is performance. However, just as all nondeterministic functions are secretly deterministic, so are all dynamically-typed languages secretly statically-typed. Performance differences between the two language families should therefore level out around the time Python changes its name to HAL 9000.

The virtual machines of dynamic languages like Python implement some idealized logical machine, and don't necessarily correspond very closely to any real physical hardware. The Java virtual machine, in contrast, is more similar in functionality to a classical C compiler, except that instead of emitting machine instructions, it executes built-in routines. In Python, an integer is a Python object with a bunch of attributes and methods attached to it. In Java, an int is a designated number of bits, usually 32. It's not really a fair comparison. Python integers should really be compared to the Java Integer class. Java's "int" primitive data type can't be compared to anything in the Python language, because the Python language simply lacks this layer of primitives, and so does Python bytecode.

Because Java variables are explicitly typed, one can reasonably expect something like Jython performance to be in the same ballpark as cPython. On the other hand, a Java virtual machine implemented in Python is almost guaranteed to be slower than mud. And don't expect Ruby, Perl, etc., to fare any better. They weren't designed to do that. They were designed for "scripting", which is what programming in a dynamic language is called.

Every operation that takes place in a virtual machine eventually has to hit real hardware. Virtual machines contain pre-compiled routines which are general enough to to execute any combination of logical operations. A virtual machine may not be emitting new machine instructions, but it certainly is executing its own routines over and over in arbirtrarily complex sequences. The Java virtual machine, the Python virtual machine, and all the other general-purpose virtual machines out there are equal in the sense that they can be coaxed into performing any logic you can dream up, but they are different in terms of what tasks they take on, and what tasks they leave to the programmer.

Psyco for Python is not a full Python virtual machine, but a just-in-time compiler that hijacks the regular Python virtual machine at points it thinks it can compile a few lines of code -- mainly loops where it thinks the primitive type of some variable will remain constant even if the value is changing with each iteration. In that case, it can forego some of the incessent type determination of the regular virtual machine. You have to be a little careful, though, lest you pull the type out from under Psyco's feet. Pysco, however, usually knows to just fall back to the regular virtual machine if it isn't completely confident the type won't change.

The moral of the story is that primitive data type information is really helpful to a compiler/virtual machine.

Finally, to put it all in perspective consider this: a Python program executed by a Python interpreter/virtual machine implemented in Java running on a Java interpreter/virtual machine implemented in LLVM running in a qemu virtual machine running on an iPhone.


```

# .pyc Files
`python3 -m compileall . -q` will compile all `.py` files in your directory into `.pyc` files.

`.pyc` files are compiled bytecode files generated by the Python Interpreter from your `.py` files.  Whenever you run `.py` files, this process happens directly afterwards under the hood.
- These files can be ran over and over again, so no need to recompile the source code every time the script is run if it hasn't changed.
- They're stored in the same directory as the `.py` files.
- `.pyc` files are specific to the versin of Python that was used to generate them.

The Python Virtual Machine is what runs these `.pyc` files.  Computers can only understand machine (binary) code, so the PVM translates that bytecode in the `.pyc` files into machine code that the computer can run.
- The interpreter in the PVM has to translate the program one line at a time to determine the variable types, which consumes a lot of time.  Whereas in statically typed languages like Java this process is already completed from the beginning because developers are forced to define the data types for all of their variables.
- CPython is typically the default Python Interpreter, as shown in the filename of the `.pyc` file - `__pycache__/recommendation.cpython-38.pyc`.

The flow is as follows:
1. Developer writes source code
2. When ready for execution, you run the `.py` file
3. This kicks off a process to compile the source code in the `.py` file into bytecode in a `.pyc` file.
   1. If the file hasn't changed, then this compilation step doesn't need to be repeated and can be skipped.
4. The interpreter then reads through the bytecode in the `.pyc` file line by line to execute the program in the Python Virtual Machine.