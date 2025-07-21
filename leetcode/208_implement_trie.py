class Trie:
    def __init__(self):
        self.existing_words = set()

    def insert(self, word: str) -> None:
        if word not in self.existing_words:
            self.existing_words.add(word)

        return

    def search(self, word: str) -> bool:
        return True if word in self.existing_words else False

    def startsWith(self, prefix: str) -> bool:
        return any(word.startswith(prefix) for word in self.existing_words)


# Your Trie object will be instantiated and called as such:
# obj = Trie()
# obj.insert(word)
# param_2 = obj.search(word)
# param_3 = obj.startsWith(prefix)

words = {"pref", "prefix"}
prefix = "pref"

for word in words:
    if word.startswith(prefix):
        print(f"Word match at {word}")


# the actual tree method but i really do not give 2 fucks lmfao
# class Trie:
#     def __init__(self):
#         self.root = TrieNode()

#     def insert(self, word: str) -> None:
#         node = self.root
#         for char in word:
#             # insert char if not present
#             if char not in node.children:
#                 node.children[char] = TrieNode()
#             node = node.children[char]
#         node.is_end_of_word = True

#     def search(self, word: str) -> bool:
#         node = self.root
#         for char in word:
#             if char not in node.children:
#                 return False
#             node = node.children[char]
#         return node.is_end_of_word

#     def startsWith(self, prefix: str) -> bool:
#         node = self.root
#         for char in prefix:
#             if char not in node.children:
#                 return False
#             node = node.children[char]
#         return True
