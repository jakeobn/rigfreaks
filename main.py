from app import app  # noqa: F401
from prebuilt_configs import create_prebuilt_configs

# Add init_build route
from init_pc_build import update_app_route, add_all_components_to_session
update_app_route()

# Load prebuilt configurations and initialize default PC build when the app starts
with app.app_context():
    create_prebuilt_configs()
    add_all_components_to_session()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
