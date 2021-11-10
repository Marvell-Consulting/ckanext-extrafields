# see https://docs.ckan.org/en/2.9/extensions/adding-custom-fields.html for reference
# See https://github.com/okfn/ckanext-example
import logging
from ckan import plugins
from ckan.logic import NotFound
from ckan.common import c
from ckan.lib.base import model

toolkit = plugins.toolkit

log = logging.getLogger(__name__)

CAPABILITY_VOCAB = u"capabilities"


def create_capabilities_tags():
    capability_tags = [
        u"Appointment or Scheduling",
        u"Referrals",
        u"Access to Records",
        u"Clinical Decision Support",
        u"Continuity of Care",
        u"Demographics",
        u"Key Care Information",
        u"Medication Management",
        u"Prescribing",
        u"Dispensing",
        u"Vaccination",
        u"Messaging",
        u"Patient Communication",
        u"Reference Data",
        u"Information Governance",
        u"Security",
        u"Tests and Diagnostics",
    ]
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    try:
        data = {"id": CAPABILITY_VOCAB}
        toolkit.get_action("vocabulary_show")(context, data)
    except toolkit.ObjectNotFound:
        data = {"name": "capabilities"}
        vocab = toolkit.get_action("vocabulary_create")(context, data)
        for tag in capability_tags:
            data = {"name": tag, "vocabulary_id": CAPABILITY_VOCAB}
            toolkit.get_action("tag_create")(context, data)


def capabilities():
    create_capabilities_tags()
    try:
        tag_list = toolkit.get_action("tag_list")
        capability_tags = tag_list(data_dict={"vocabulary_id": CAPABILITY_VOCAB})
        return capability_tags
    except toolkit.ObjectNotFound:
        return None


class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurer)
    # plugins.implements(plugins.IValidators)

    # TODO: this can probably all go in favour of schema flow
    def setup_template_variables(self, context, data_dict=None):
        """
        Adds variables to c just prior to the template being rendered that can
        then be used within the form
        """
        c.resource_columns = model.Resource.get_columns()
        try:
            c.capability_tags = toolkit.get_action("tag_list")(
                context, {"vocabulary_id": CAPABILITY_VOCAB}
            )

            c.vocab_info = toolkit.get_action("vocabulary_show")(
                {}, {"id": CAPABILITY_VOCAB}
            )["id"]

        except NotFound:
            c.capability_tags = None

    # IConfigurer
    # This interface allows to implement a function update_config()
    # that allows us to update the CKAN config, in our case we want to
    # add an additional location for CKAN to look for templates.
    def update_config(self, config):
        # toolkit.add_template_directory(config_, 'templates')
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
        capability_vocab_id = toolkit.get_action("vocabulary_show")(
            {}, {"id": CAPABILITY_VOCAB}
        )["id"]

        schema.update(
            {
                # this doesn't work (using vocab name)
                "capabilities_selected": [
                    # toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_from_tags")(
                        str(capability_vocab_id)
                    ),
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
