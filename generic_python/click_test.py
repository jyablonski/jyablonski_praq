# https://click.palletsprojects.com/en/stable/options/#name-your-options
import click


def print_test() -> None:
    print("___")
    return None


# group can contain multiple cli.command objects
@click.group()
def cli():
    pass


@cli.command()
def initdb():
    click.echo("Initialized the database")


@cli.command()
def dropdb():
    click.echo("Dropped the database")


# click.echo() is a little more robust than print statements in case something

# Click is based on declaring commands through decorators.
# you get `help` parameters out of the box


# At its simplest, just decorating a function with this `click.command()` decorator will make it into a callable script
@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option(
    "--name",
    default="tester mctesterson",
    prompt="Your name",
    help="The person to greet.",
    required=True,
    show_default=True,
)
@click.option("--extra_dings", is_flag=True)
def hello(count: int, name: str, extra_dings: bool):
    """Simple program that greets NAME for a total of COUNT times."""
    output = f"Hello {name}!"
    if extra_dings:
        output += " !!!"
    for _ in range(count):
        click.echo(message=output)
        print_test()


if __name__ == "__main__":
    hello()
