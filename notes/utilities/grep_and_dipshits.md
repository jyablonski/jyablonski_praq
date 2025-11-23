# grep

```sh
# search for all python files in the current directory & below that contain the statements at the end
grep -r --include "*.py" "import json"
grep -r --include "*.py" "global"

# same as above, but exclude any directories named `site-packages` that it finds
grep -r --include "*.py" --exclude-dir "site-packages" "import json"
grep -r --include "*.py" --exclude-dir "site-packages" "global"

# same as above, but we pass in an absolute path at the end to search for
grep -r --include "*.py" --exclude-dir "site-packages" "global" ~/Documents/
```
