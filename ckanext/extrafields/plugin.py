# see https://docs.ckan.org/en/2.9/extensions/adding-custom-fields.html for reference
from ckan import plugins
from ckan.plugins.toolkit import Invalid

toolkit = plugins.toolkit


def create_country_codes():
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': 'country_codes'}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        data = {'name': 'country_codes'}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        for tag in (u'uk', u'ie', u'de', u'fr', u'es'):
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)


def country_codes():
    create_country_codes()
    try:
        tag_list = toolkit.get_action('tag_list')
        country_codes = tag_list(data_dict={'vocabulary_id': 'country_codes'})
        return country_codes
    except toolkit.ObjectNotFound:
        return None


def create_capabilities_tags():
    capability_tags = [
        u'Appointment or Scheduling',
        u'Referrals',
        u'Access to Records',
        u'Clinical Decision Support',
        u'Continuity of Care',
        u'Demographics',
        u'Key Care Information',
        u'Medication Management',
        u'Prescribing',
        u'Dispensing',
        u'Vaccination',
        u'Messaging',
        u'Patient Communication',
        u'Reference Data',
        u'Information Governance',
        u'Security',
        u'Tests and Diagnostics'
    ]
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': 'capabilities'}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        data = {'name': 'capabilities'}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        for tag in capability_tags:
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)


def capabilities():
    create_capabilities_tags()
    try:
        tag_list = toolkit.get_action('tag_list')
        capability_tags = tag_list(data_dict={'vocabulary_id': 'capabilities'})
        return capability_tags
    except toolkit.ObjectNotFound:
        return None


def country_codes():
    create_country_codes()
    try:
        tag_list = toolkit.get_action('tag_list')
        country_codes = tag_list(data_dict={'vocabulary_id': 'country_codes'})
        return country_codes
    except toolkit.ObjectNotFound:
        return None


def ralph_only(value, context):
    if value and context['user'] != 'ralph':
        raise Invalid('only ralph may set this value')
    return value


class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer
    # This interface allows to implement a function update_config()
    # that allows us to update the CKAN config, in our case we want to
    # add an additional location for CKAN to look for templates.
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)

    # IConfigurer
    def update_config(self, config):
        # toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic',
        #                      'extrafields')
        toolkit.add_template_directory(config, 'templates')

        def _modify_package_schema(self, schema):
            # Add our custom country_code metadata field to the schema.
            schema.update({
                'country_code': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_tags')('country_codes')],
                'capabilities':  [toolkit.get_validator('ignore_missing'),
                                  toolkit.get_converter('convert_to_tags')('capabilities')]
            })
            # Add our custom_test metadata field to the schema, this one will use
            # convert_to_extras instead of convert_to_tags.
            schema.update({
                'custom_text': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')]
            })
            # Add our custom_resource_text metadata field to the schema
            schema['resources'].update({
                'custom_resource_text': [toolkit.get_validator('ignore_missing')]
            })
            return schema

    def show_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).show_package_schema()
        schema.update({
            'custom_text': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(
            toolkit.get_converter('free_tags_only'))

        # Add our custom country_code metadata field to the schema.
        schema.update({
            'country_code': [
                toolkit.get_converter('convert_from_tags')('country_codes'),
                toolkit.get_validator('ignore_missing')],
            'capabilities':  [toolkit.get_validator('ignore_missing'),
                              toolkit.get_converter('convert_to_tags')('capabilities')]
        })

        # Add our custom_text field to the dataset schema.
        schema.update({
            'custom_text': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })

        schema['resources'].update({
            'custom_resource_text': [toolkit.get_validator('ignore_missing')]
        })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # IValidators
    def get_validators(self):
        return {
            u'ralph_only': ralph_only
        }

    plugins.implements(plugins.ITemplateHelpers)

    def get_helpers(self):
        return {'country_codes': country_codes,
                'capabilities': capabilities}
