# Regex

Python's `re` module provides tools to work with regular expressions. Start by importing it:

```python
import re
```

#### 2. **Basic Syntax**

- **`re.match(pattern, string)`**: Matches at the beginning of the string.
- **`re.search(pattern, string)`**: Searches the string for a match.
- **`re.findall(pattern, string)`**: Returns all matches in a list.
- **`re.sub(pattern, repl, string)`**: Substitutes matches with a replacement string.

Example:

```python
text = "The quick brown fox jumps over the lazy dog."
pattern = r"\bfox\b"  # Word boundary to match "fox" exactly

match = re.search(pattern, text)
if match:
    print("Match found:", match.group())
else:
    print("No match")
```

#### 3. **Common Patterns**

1. **Character Classes**:

   - `\d`: Any digit (0-9).
   - `\D`: Non-digit.
   - `\w`: Any word character (alphanumeric + underscore).
   - `\W`: Non-word character.
   - `\s`: Any whitespace.
   - `\S`: Non-whitespace.

1. **Quantifiers**:

   - `*`: Zero or more.
   - `+`: One or more.
   - `?`: Zero or one.
   - `{n}`: Exactly `n` occurrences.
   - `{n,}`: At least `n` occurrences.
   - `{n,m}`: Between `n` and `m` occurrences.

1. **Anchors**:

   - `^`: Start of a string.
   - `$`: End of a string.

1. **Groups and Captures**:

   - `(pattern)`: Capturing group.
   - `(?:pattern)`: Non-capturing group.

1. **Special Sequences**:

   - `|`: Logical OR.
   - `.`: Matches any character except a newline.

#### 4. **Testing Examples**

- **Validate an Email Address**:

  ```python
  email_pattern = r"^[\w.-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
  email = "example.email@test-domain.com"

  if re.match(email_pattern, email):
      print("Valid email!")
  else:
      print("Invalid email.")
  ```

- **Extract All URLs from Text**:

  ```python
  text = "Visit us at https://example.com or http://test.org"
  url_pattern = r"https?://[^\s]+"

  urls = re.findall(url_pattern, text)
  print("Extracted URLs:", urls)
  ```

- **Split a String by Multiple Delimiters**:

  ```python
  text = "apple;orange|banana,grape"
  delimiters = r"[;,|]"

  result = re.split(delimiters, text)
  print(result)
  ```

#### 5. **Using Online Tools for Regex Testing**

1. **[Regex101](https://regex101.com/):**

   - Explains your pattern step-by-step.
   - Allows testing with real-time feedback.
   - Supports Python flavor.

1. **[RegExr](https://regexr.com/):**

   - A user-friendly interface for learning and testing regex.

1. **Python REPL or Jupyter Notebooks**:

   - Experiment interactively with Python's `re` module.

#### 6. **Tips for Implementation**

- Use **raw strings (`r"pattern"`)** to avoid escaping backslashes (`\\`).

- Use **named groups (`(?P<name>pattern)`)** for easier readability:

  ```python
  pattern = r"(?P<protocol>https?)://(?P<domain>[^\s/]+)"
  match = re.search(pattern, "https://example.com")
  if match:
      print("Protocol:", match.group("protocol"))
      print("Domain:", match.group("domain"))
  ```

- Test regex thoroughly to cover edge cases:

  ```python
  test_cases = ["abc123", "123abc", "abc-123"]
  pattern = r"^[a-z]+\d+$"

  for case in test_cases:
      print(f"Testing '{case}':", bool(re.match(pattern, case)))
  ```

- **Compile patterns** for repeated use:

  ```python
  compiled_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")  # SSN pattern
  data = "123-45-6789 is a valid SSN, but 123456789 is not."

  print(compiled_pattern.findall(data))
  ```

Would you like me to elaborate on a specific use case or tool?
