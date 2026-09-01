from datetime import datetime

import typer

from .core import Store, left, mk
from .ui import Clock

app = typer.Typer(help="terminal alarm clock")


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context):
  
    if ctx.invoked_subcommand is None:
        Clock().run()


@app.command()
def set(
    t: str,
    label: str = typer.Argument("alarm"),
    tom: bool = typer.Option(False, "--tom", help="set for tomorrow"),
):
    """set an alarm, e.g. alarm set 18:30 dinner"""
    try:
        at = mk(t, days=1 if tom else 0)
    except ValueError as e:
        typer.secho(f"error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    a = Store().add(at, label)
    typer.echo(f"alarm {a.id} set — {a.at:%a %d %b %H:%M} ({left(a.at)}) {label}")


@app.command()
def list():
  
    s = Store()
    now = datetime.now()
    if not s.rows:
        typer.echo("no alarms")
        return
    typer.echo(f"{'id':>3}  {'when':<16}  {'left':>10}  label")
    for a in sorted(s.rows, key=lambda a: a.at):
        st = "due" if a.due(now) else left(a.at, now)
        typer.echo(f"{a.id:>3}  {a.at:%a %d %b %H:%M}  {st:>10}  {a.label}")


@app.command()
def cancel(nid: int):
   
    if Store().cancel(nid):
        typer.echo(f"alarm {nid} cancelled")
    else:
        typer.secho(f"error: no alarm {nid}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def run():

    Clock().run()


def main():
    app()
