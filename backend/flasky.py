# -*- coding: utf-8 -*-
import logging
import os

from app.event import *
from app.utils.common import get_local_ip
from app.utils.logger import setup_logging
from dotenv import load_dotenv

# 初始化全局日志系统
setup_logging()

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
logging.info(f"加载环境变量文件: {dotenv_path}")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 开发环境自动获取本地地址
if os.getenv("FLASK_DEBUG"):
    os.environ["FLASK_RUN_HOST"] = get_local_ip()

COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage

    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()

import sys

import click
from app import create_app, db, socketio
from app.models import (
    Comment,
    Follow,
    Log,
    Permission,
    Post,
    Praise,
    Role,
    User,
    Image,
    PostType,
    ImageType,
)
from flask_migrate import Migrate, upgrade

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Follow=Follow,
        Role=Role,
        Permission=Permission,
        Post=Post,
        Comment=Comment,
        Praise=Praise,
        Log=Log,
        Image=Image,
        PostType=PostType,
        ImageType=ImageType,
    )


@app.cli.command()
@click.option(
    "--coverage/--no-coverage", default=False, help="Run tests under code coverage."
)
@click.argument("test_names", nargs=-1)
def test(coverage, test_names):
    """Run the unit tests."""
    if coverage and not os.environ.get("FLASK_COVERAGE"):
        import subprocess

        os.environ["FLASK_COVERAGE"] = "1"
        sys.exit(subprocess.call(sys.argv))

    import unittest

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "tmp/coverage")
        COV.html_report(directory=covdir)
        print("HTML version: file://%s/index.html" % covdir)
        COV.erase()


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

    # create or update user roles
    Role.insert_roles()

    # ensure all users are following themselves
    User.add_self_follows()


@app.cli.command("add")
@click.argument("some")
def add(some):
    print(some)


if __name__ == "__main__":
    socketio.run(
        app, host=os.getenv("FLASK_RUN_HOST"), port=os.getenv("FLASK_RUN_PORT")
    )
