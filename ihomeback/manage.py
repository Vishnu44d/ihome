import click


@click.group()
def cli():
    '''Welcome the to cli for managing Server'''
    pass


@click.command()
def initdb():
    from server import engine, createTables
    createTables(engine)
    click.echo('Initialized the database')


@click.command()
def dropdb():
    from server import engine, destroyTables
    destroyTables(engine)
    click.echo('Dropped the database')


cli.add_command(initdb)
cli.add_command(dropdb)


if __name__ == '__main__':
    cli()
