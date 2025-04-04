import click


# usage: `python click/main.py --s3-file s3://test-bucket/test-file.csv`
@click.command()
@click.option("--s3-file", required=True, help="S3 Path to the input file")
def generate_statement(s3_file: str) -> None:
    click.echo(f"Generating Statement for {s3_file}")
    return None


if __name__ == "__main__":
    generate_statement()
