from . import create_app


# Use DevelopmentConfig by default so a local SQLite DB URI is available
# when running the module directly.
app = create_app('flasky.config.DevelopmentConfig')


if __name__ == '__main__':
    app.run(debug=True)
