import os
import sys
sys.path.insert(0, '.')
try:
    from config import Config as conf
except ImportError:
    from .config import config
    conf = config[os.getenv('LV_ENV') or 'default']

from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand
from flask_admin import Admin
from flask_whooshalchemyplus import whoosh_index

from blog import create_app, db, make_celery, celery as celery_worker, migrate
from blog.models.comments import Comment
from blog.models.users import User
from blog.models.posts import Post
from blog.models.roles import Role, Permission

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()
if os.path.exists('.env'):
    print('Importing environment from .env')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

app = create_app(conf)
basedir = os.path.abspath(os.path.dirname(__file__))
manager = Manager(app)
whoosh_index(app, Post)
admin = Admin(app, name='Cong Blog', template_mode="bootstrap3")
celery = make_celery(app, celery_worker)

@app.teardown_appcontext
def shutdown_session(exception=None):
    return db.session.remove()


def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Role=Role,
        Comment=Comment,
        Permission=Permission,
        Post=Post)

manager.add_command("shell",
                    Shell(use_ipython=True, make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def deploy():
    Role.insert_roles()
    user = User(
        email='lv.cong@gmail.com',
        username='Lv Cong',
        password='5f4dcc3b5aa765d61d8327deb882cf99',
        confirmed=True)
    role = Role.query.filter_by(name='Administrator').first()
    user.role = role
    user.save()


@manager.command
def test(coverage=False):
    """Run the unit tests"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover(
        'blog/tests', pattern='test_*.py')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


def cli():
    manager.run()
