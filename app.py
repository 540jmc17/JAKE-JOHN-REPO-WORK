"""Run the CampusGear web application with: flask --app app run --debug"""
"""
CampusGear - Main Applicaiton Entry Point

This file starts the CampusGear Website using Flask.
It connects to the main application setup and allows
The website to run on a local development server.
"""

# Import the create_app function from the campusgear package.
# This function sets up the Flask application and its routes.
from campusgear import create_app

# Create the CampusGear application using the imported function.
app = create_app()


# Run the Flask development server when this file is executed directly.
# This allows developers to test the website locally.
if __name__ == "__main__":
    app.run()
