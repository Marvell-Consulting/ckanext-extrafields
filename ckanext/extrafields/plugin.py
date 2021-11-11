# see https://docs.ckan.org/en/2.9/extensions/adding-custom-fields.html for reference
# See https://github.com/okfn/ckanext-example
import logging
from ckan import plugins
from ckan.logic import NotFound
from ckan.common import c
from ckan.lib.base import model

from .helpers import capabilities, CAPABILITY_VOCAB

toolkit = plugins.toolkit

log = logging.getLogger(__name__)


class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurer)

    # IConfigurer
    # This interface allows to implement a function update_config()
    # that allows us to update the CKAN config, in our case we want to
    # add an additional location for CKAN to look for templates.

    def update_config(self, config):
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic',
        #                      'extrafields')
        toolkit.add_template_directory(config, "templates")

    # IDatasetForm

    def _modify_package_schema(self, schema):
        # Add our custom_test metadata field to the schema, this one will use
        # convert_to_extras instead of convert_to_tags.
        schema.update(
            {
                "capabilities": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_tags")(CAPABILITY_VOCAB),
                ]
            }
        )

        return schema

    def create_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    # get stuff from the database and return it in a manner
    # that is useful for the form
    def show_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).show_package_schema()
        schema["tags"]["__extras"].append(toolkit.get_converter("free_tags_only"))

        # get capabilities ID in order to filter tags
        # capability_vocab_id = toolkit.get_action("vocabulary_show")(
        #     {}, {"id": CAPABILITY_VOCAB}
        # )["id"]

        schema.update(
            {
                "capabilities_selected": [
                    # TODO: why does ignore_missing cut out selected capabilities?
                    # toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_from_tags")(CAPABILITY_VOCAB),
                ]
            }
        )

        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # ITemplateHelpers

    def get_helpers(self):
        return {"capabilities": capabilities}
