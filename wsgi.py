from app import create_app  # o desde donde crees tu app Flask

app = create_app()

if __name__ == "__main__":
    app.run()