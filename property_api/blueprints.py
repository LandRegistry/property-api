# Import every blueprint file
from property_api.views import general


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)

    # All done!
    app.logger.info("Blueprints registered")
