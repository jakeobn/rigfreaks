from app import app  # noqa: F401
from prebuilt_configs import create_prebuilt_configs

# Load prebuilt configurations when the app starts
with app.app_context():
    create_prebuilt_configs()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
