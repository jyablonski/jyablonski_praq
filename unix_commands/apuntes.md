# Unix OS Commands

## Basic
1. **`pwd` (Print Working Directory):** This command shows you the current directory (folder) you are in.

   Example:
   ```
   pwd
   ```

2. **`ls` (List):** List the files and directories in the current directory.

   Example:
   ```
   ls
   ```

3. **`cd` (Change Directory):** Change your current directory to the specified directory.

   Example:
   ```
   cd /path/to/directory
   ```

4. **`mkdir` (Make Directory):** Create a new directory.

   Example:
   ```
   mkdir new_directory
   ```

5. **`rmdir` (Remove Directory):** Remove an empty directory.

   Example:
   ```
   rmdir empty_directory
   ```

6. **`rm` (Remove):** Delete files or directories. Be cautious, as it doesn't move items to the trash, and deleted files cannot usually be easily recovered.

   Example (remove a file):
   ```
   rm file.txt
   ```

   Example (remove a directory and its contents):
   ```
   rm -r directory_name
   ```

7. **`touch`:** Create an empty file.

   Example:
   ```
   touch new_file.txt
   ```

8. **`cp` (Copy):** Copy files or directories from one location to another.

   Example:
   ```
   cp file.txt /path/to/destination
   ```

9. **`mv` (Move):** Move or rename files and directories.

   Example (rename a file):
   ```
   mv old_name.txt new_name.txt
   ```

   Example (move a file to a different directory):
   ```
   mv file.txt /new_directory
   ```

10. **`cat` (Concatenate):** Display the contents of a file in the terminal.

   Example:
   ```
   cat file.txt
   ```

11. **`more` or `less`: Paginate through a long text file one screen at a time.

   Example (using `more`):
   ```
   more file.txt
   ```

12. **`head` and `tail`:** Display the beginning or end of a file.

   Example (show the first 10 lines of a file):
   ```
   head -n 10 file.txt
   ```

   Example (show the last 10 lines of a file):
   ```
   tail -n 10 file.txt
   ```

13. **`man` (Manual):** Access the manual pages for commands to learn more about their usage.

   Example:
   ```
   man ls
   ```

## Advanced
Some more advanced Unix/Linux commands include: `grep`, `sed`, and `awk`. These commands are powerful tools for text processing and manipulation.

### `grep` (Global Regular Expression Print):

`grep` is used for searching text using regular expressions. It can be used to search for patterns or specific strings in files or the output of other commands.

**Basic Usage:**
```
grep pattern file.txt
```

- `pattern` is the text or regular expression you want to search for.
- `file.txt` is the file you want to search in.

**Example 1: Searching for a Word in a File**
Suppose you have a file named `example.txt`, and you want to find all occurrences of the word "apple" in that file:

```bash
grep "apple" example.txt
```

**Example 2: Searching in Multiple Files**
You can search for a pattern in multiple files using wildcards:

```bash
grep "pattern" *.txt
```

### `sed` (Stream Editor):

`sed` is a text stream editor that is used for text manipulation, such as search and replace, deletion, insertion, and more.

**Basic Usage:**
```
sed 's/old_text/new_text/' input.txt > output.txt
```

- `old_text` is the text you want to replace.
- `new_text` is the replacement text.
- `input.txt` is the input file.
- `output.txt` is the file where the modified text will be saved.

**Example 1: Replacing Text**
Suppose you have a file `input.txt`, and you want to replace all occurrences of "apple" with "banana" and save the result in `output.txt`:

```bash
sed 's/apple/banana/' input.txt > output.txt
```

### `awk`:

`awk` is a versatile text processing tool that operates on data files and allows you to perform a wide range of text manipulation and processing tasks.

**Basic Usage:**
```
awk 'pattern { action }' input.txt
```

- `pattern` is a condition or regular expression to match lines.
- `{ action }` is a block of code to be executed on lines that match the pattern.
- `input.txt` is the input file.

**Example 1: Print Specific Fields from a CSV File**
Suppose you have a CSV file with the following content:

```csv
Name,Age,City
Alice,25,New York
Bob,30,Los Angeles
Charlie,28,Chicago
```

You can use `awk` to print only the names and cities:

```bash
awk -F ',' '{print $1, $3}' input.csv
```

In this example, `-F ','` specifies that the input file is comma-separated (CSV). The `{print $1, $3}` block prints the first and third fields (Name and City).


1. **`find`:** Used to search for files and directories based on various criteria, such as name, size, modification time, and more.

   Example:
   ```
   find /path/to/search -name "*.txt"
   ```

2. **`tar`:** Used for creating and extracting archive files. It's often used for compressing multiple files or directories into a single archive.

   Example (create a tarball):
   ```
   tar -czvf archive.tar.gz directory/
   ```

   Example (extract a tarball):
   ```
   tar -xzvf archive.tar.gz
   ```

3. **`rsync`:** A powerful tool for copying and synchronizing files and directories, often used for efficient data transfer and backup tasks.

   Example (copy files between local and remote hosts):
   ```
   rsync -avz source_directory/ user@remote_host:/destination_directory/
   ```

4. **`curl` and `wget`:** Used for downloading files from the web. They can fetch files via HTTP, HTTPS, FTP, and more.

   Example (using `curl`):
   ```
   curl -O https://example.com/file.txt
   ```

5. **`dd`:** A command for low-level copying and conversion of data. It is often used for tasks like creating bootable USB drives.

   Example (create a bootable USB drive from an ISO image):
   ```
   dd if=image.iso of=/dev/sdX bs=4M
   ```

6. **`top` and `htop`:** Tools for monitoring system performance, displaying real-time information about processes, CPU usage, memory, and more.

   Example (using `top`):
   ```
   top
   ```

7. **`nohup`:** Allows you to run a command that continues running even after you log out. It's useful for long-running processes.

   Example:
   ```
   nohup command-to-run &
   ```

8. **`screen` and `tmux`:** Terminal multiplexers that allow you to run multiple terminal sessions within a single terminal window, detach and reattach sessions, and more.

   Example (using `tmux` to create and manage sessions):
   ```
   tmux
   ```

9. **`iptables`:** A powerful tool for configuring and managing firewall rules on Linux systems.

   Example (allow SSH traffic):
   ```
   iptables -A INPUT -p tcp --dport 22 -j ACCEPT
   ```

10. **`grep`, `sed`, and `awk` (as previously discussed):** These commands offer advanced text processing and manipulation capabilities.

These are just a few examples of advanced Unix/Linux commands. The Unix command-line environment provides a rich set of tools for various tasks, and learning how to use them can greatly enhance your productivity and system administration capabilities. It's often beneficial to explore and become proficient in the commands that are most relevant to your specific use cases and needs.


### Curl vs wget
`curl` and `wget` are both command-line tools used for downloading files from the web, but they have some differences in their features and capabilities:

**`curl` (cURL):**

1. **URL Support:** `curl` supports a wide range of URL schemes, including HTTP, HTTPS, FTP, FTPS, SCP, SFTP, LDAP, and more. It's a versatile tool for making network requests and supports a variety of protocols.

2. **Flexible Output:** `curl` can send the downloaded content to the standard output or save it to a file. It's a more flexible tool for working with the downloaded data.

3. **Header Retrieval:** `curl` can retrieve and display response headers and allows you to set custom headers for your requests.

4. **Multiple URLs:** `curl` can handle multiple URLs in a single command.

5. **Parallel Downloads:** `curl` supports parallel downloads when used with multiple URLs.

**`wget`:**

1. **Simpler Usage:** `wget` is known for its straightforward and user-friendly syntax. It's often considered easier to use for basic downloading tasks.

2. **Recursive Downloads:** `wget` can recursively download entire websites, which is useful for mirroring or downloading a website's content for offline viewing.

3. **Resuming Downloads:** `wget` can resume interrupted downloads, allowing you to continue downloading large files from where they left off.

4. **Timestamp Checking:** `wget` checks for differences in file timestamps on the server and locally, making it useful for keeping local copies up to date.

5. **FTP Support:** `wget` provides good support for FTP downloads.

In summary, `curl` is a more feature-rich and versatile tool for making network requests and downloading files from the web. It excels at handling various protocols and supports complex use cases. On the other hand, `wget` is known for its simplicity, user-friendly syntax, and features like recursive downloads and resuming interrupted downloads. The choice between `curl` and `wget` depends on your specific needs and preferences. You can use either tool based on the requirements of your downloading tasks.