# ASCII

The original system.  Every letter, digit, and symbol (a-z, 0-9, +, =, / etc) is represented as a number between 32 and 127.  Most computers back in the day used 8-bit bytes so a byte could store 255 numbers.

Downside is this only worked for the english system.  Wanted to use foreign langugage characters?  You're out of luck.

ASCII supports 128 character code points.

# Unicode

Unicode is a character set standard used to represent characters from many different human languages.  Unicode translates characters into numbers.

Each character is represented via Unicode "code points", aka `U+00639`. These Unicode values can then be converted into binary `01101100 01001001`.  

When we store data to memory or hard drives they cannot tell whether `01101100 01001001` refers to the same (large) number or 2 different numbers. This is where UTF-8 comes in.

Things like emojis can easily be added in `U+1F9D1 🧑`.

# UTF-8

UTF-8 is a method for encoding Unicode characters in a way that computers can sensibly understand (binary digits).  Encoding translates numbers into binary.

UTF-8 is an encoding scheme.  UTF-8 is backwards compatible with ASCII.  There's also UTF-16 and UTF-32.  

In UTF-8, every code point from 0-127 is stored as a single byte.  Beyond that, they use 2, 3, 4, and up to 6 bytes to store additional code points.  UTF-8 can store 1,112,064 valid character code points.  

UTF-8 allows people using English language to continue as normal, but it also allows every character possible across all human languages to be represented under 1 universally accepted encoding framework.

Commonly seen in software development via stuff like `Content-Type: text/plain; charset="UTF-8" ` (in web dev).  This tells the browser the specific encoding being used.

```
A Chinese character:      汉
its Unicode value:        U+6C49
convert 6C49 to binary:   01101100 01001001
encode 6C49 as UTF-8:     11100110 10110001 10001001
```