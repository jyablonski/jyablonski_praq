# Git Apuntes

### Reverting a Commit
Run the following commands:
1. `git reset --hard HEAD~1`
2. `git push origin +HEAD^:jacob`


`--hard` means it will automatically get rid of all unstaged changes you have.  Use `--soft` if you don't want this behavior