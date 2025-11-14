"""Utility to create the local development database (SQLite).

Run this script from the repository root to create the DB file and tables.
"""
from flasky import create_app
from flasky.app import db


def main():
    app = create_app('flasky.config.DevelopmentConfig')
    with app.app_context():
        db.create_all()
        print('Database and tables created (DevelopmentConfig)')


if __name__ == '__main__':
    main()
