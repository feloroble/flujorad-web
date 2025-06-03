from app import create_app
from app.extensions import db
from flask_migrate import Migrate

app = create_app()

# Esto permite usar flask db desde línea de comandos
from flask.cli import with_appcontext
import click

@app.cli.command("create-db")
@with_appcontext
def create_db():
    db.create_all()
    click.echo("Base de datos creada.")


if __name__ == "__main__":
    app.run(debug=True)
