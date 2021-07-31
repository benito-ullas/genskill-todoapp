import psycopg2 
from flask import current_app, g
import click 
from flask.cli import with_appcontext

def get_db():
        if 'db' not in g:
                dbname = current_app.config.from_envvar['DATABASE_URL']
                g.db = psycopg2.connect(f"dbname={dbname}")
        return g.db
        
def init_db():
    db = get_db()
    # Create the tables
    f = current_app.open_resource("sql/data.sql")
    sql_code = f.read().decode("ascii")
    cur = db.cursor()
    cur.executescript(sql_code)
    cur.close()
    db.commit()



    click.echo("Database created")
    cur.close()
    db.commit()
    close_db()

@click.command('initdb', help="initialise the database")
@with_appcontext
def init_db_command():
    init_db()
    click.echo('DB initialised') 

