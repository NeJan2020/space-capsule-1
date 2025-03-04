import click

from resources.scenes.service_loss import case3
from resources.scenes.service_slow import case2, case1
from spacecapsule.history import list_experiment, show_experiment, undo_experiment


@click.group()
def cli():
    pass


@click.command()
def history():
    list_experiment()


@click.command()
@click.argument('experiment')
def show(experiment):
    show_experiment(experiment)


@click.command()
@click.argument('experiment')
def undo(experiment):
    undo_experiment(experiment)


cli.add_command(history)
cli.add_command(show)
cli.add_command(undo)

# cli.add_command(resource)
# cli.add_command(loss)
# cli.add_command(cpu)
# cli.add_command(diskfill)
cli.add_command(case1)
cli.add_command(case2)
cli.add_command(case3)
if __name__ == '__main__':
    cli()
