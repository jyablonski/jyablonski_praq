# each parent node is typically a class (or an instance of one), used to group related functionality and expose intuitive APIs
# Classes act as namespaces for grouping related methods.
class Completions:
    def create(self, messages):
        print("Creating chat completion with messages:")
        for msg in messages:
            print(f"- {msg['role']}: {msg['content']}")


class Chat:
    def __init__(self):
        self.completions = Completions()


class Embeddings:
    def __init__(self):
        self._has_created_embedding = False

    def create(self, input):
        self._has_created_embedding = True
        print(f"Creating embedding for: {input}")

    @property
    def has_created_embedding(self):
        return self._has_created_embedding

    @property
    def embedding_name(self):
        print("Getting name...")
        return "Hello World"


# Client() acts as a factory that builds and wires together Chat and Completions.
class Client:
    def __init__(self):
        self.chat = Chat()
        self.embeddings = Embeddings()

    # Defines a function inside a class that does not access or modify the class or instance. It's just logically related.
    @staticmethod
    def add(x: int, y: int) -> int:
        return x + y

    # Defines a method that receives the class (cls) instead of an instance (self). Useful for alternative constructors or modifying class-level data.
    # @classmethod
    # def from_default(cls):
    #     return cls(cls.default_name)


# --- Usage ---
client = Client()

client.chat.completions.create(
    [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help?"},
    ]
)

# value of 1
client.embeddings._has_created_embedding

# create the embedding
client.embeddings.create("boobs")

# now has a value of 1
client.embeddings._has_created_embedding

client.add(4, 5)

client.embeddings
