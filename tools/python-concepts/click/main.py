import click


# example usage: `python click/main.py --s3-file s3://test-bucket/test-file.csv`
@click.command()
@click.option("--s3-file", required=True, help="S3 Path to the input file")
def generate_statement(s3_file: str) -> None:
    success = True if "test" in s3_file else False

    click.secho("📂 Starting Statement Generation...", fg="blue", bold=True)

    for i in range(1, 6):
        click.echo(f"  ➜ Running Statement {i}")

    if success:
        click.secho("✅ Statement successfully generated!", fg="green", bold=True)
    else:
        click.secho("❌ Failed to generate statement.", fg="red", bold=True)

    return None


if __name__ == "__main__":
    generate_statement()
