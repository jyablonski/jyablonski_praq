# Bash Notes
Have to run `chmod +x ./{file_name}.sh` to give permissions to execute the file.
- The `+x` command gives execution rights to the file so it can be executed.

Bash scripts start off with a Shebang (`#!/bin/bash`)

`echo` - used to display text back to the user.


All 3 methods can be used to run the file:
- `sh hello_world.sh`
- `bash hello_world.sh`
- `./hello_world.sh`

Can assign variables with `owner=jacob`, and then reference it like `echo "hello world $owner"`.

# Greeting
`./greeting.sh jacob`