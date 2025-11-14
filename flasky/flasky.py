from app import create_app

app = create_app('flasky.config.DevelopmentConfig')


if __name__ == '__main__':
    app.run(debug=True)
