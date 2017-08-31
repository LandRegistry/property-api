# Import every blueprint file
from property_api.views import general
from property_api.views.v1_0 import properties as properties_v1_0


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(properties_v1_0.properties, url_prefix='/v1/properties')

    # All done!
    app.logger.info("Blueprints registered")
