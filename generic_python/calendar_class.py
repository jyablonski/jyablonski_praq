from datetime import datetime, date


class Calendar:
    def __init__(self):
        self.events: list[str, date] = []
        self._total_events: int = 0
        # this is python sugar that the attribute here should be "private"
        # but python doesnt support this, jsut for the developers

    def add_event(self, event: str | date) -> None:
        if not isinstance(event, (str, date)):
            raise ValueError(f"Event needs to be a String or Date Object!")
        else:
            self.events.append(event)
            self._total_events += 1

    # this allows us to expose attributes of the class so devs can call them
    # using attributes instead of methods
    # `object.total_events_count`` rather than `object.total_events_count()`
    @property
    def total_events_count(self):
        return self._total_events

    @staticmethod
    def is_weekend(date: date = datetime.now().date()) -> bool:
        return date.weekday() > 4

    @classmethod
    def hello_world(cls) -> None:
        c = cls()
        print(f"hello world {c.events}")


d = Calendar()

d.add_event("hello")
d.events
d.is_weekend()
d.hello_world()

d.total_events_count
d.total_events_count = 4
