# UNIX Advanced Commands

## grep
grep can be used for file searching and pattern matching in text files.  It stands for Global Regular Expression Print.

The structure for a grep command looks like this `grep [options] pattern [file...]`
- `options:` These are various command-line options that modify the behavior of grep.
- `pattern:` This is the regular expression or plain text pattern that you want to search for. 
- `file...:` These are the files in which you want to search for the specified pattern. If no files are provided, grep reads from the standard input (e.g., you can use it with the output of another command via a pipe).

Common options include:
- i: Perform a case-insensitive match.
- r or -R: Recursively search subdirectories.
- n: Display line numbers along with the lines that match the pattern.
- c: Display only the count of lines that match the pattern.
- v: Invert the match, i.e., display lines that do not match the pattern.


``` sh
# find the number of lines in the python file that start with 'def '
grep -c 'def ' python_file.py

# can also take all of the lines and pipe them to wc -l to count them insteadssssssssss
grep 'def ' python_file.py | wc -l
```

## wc

