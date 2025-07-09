import os
from app import create_app

# Get absolute path to /templates
TEMPLATES_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')

print("🔍 Template path being used:", TEMPLATES_FOLDER)

app = create_app(template_folder=TEMPLATES_FOLDER)

if __name__ == "__main__":
    app.run(debug=True)
