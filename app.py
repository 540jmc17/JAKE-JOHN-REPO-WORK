"""Run the CampusGear web application with: flask --app app run --debug"""

from campusgear import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
