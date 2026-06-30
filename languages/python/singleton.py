# used for logging, database connections etc
class Singleton:
    _instance = None

    def __init__(self):
        # Private constructor
        if Singleton._instance is not None:
            raise Exception(
                "Singleton instance already exists. Use Singleton.get_instance() to access it."
            )
        else:
            Singleton._instance = self

    @staticmethod
    def get_instance():
        # Static method to get the singleton instance
        if Singleton._instance is None:
            Singleton._instance = Singleton()
        return Singleton._instance


b = Singleton()

# this will fail out
c = Singleton()
