from ckan.plugins.toolkit import get_action, ObjectNotFound

CAPABILITY_VOCAB = u"capabilities"


def _create_capabilities_tags():
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
    user = get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    try:
        data = {"id": CAPABILITY_VOCAB}
        get_action("vocabulary_show")(context, data)
    except ObjectNotFound:
        data = {"name": "capabilities"}
        vocab = get_action("vocabulary_create")(context, data)
        for tag in capability_tags:
            data = {"name": tag, "vocabulary_id": CAPABILITY_VOCAB}
            get_action("tag_create")(context, data)


def capabilities():
    _create_capabilities_tags()
    try:
        tag_list = get_action("tag_list")
        capability_tags = tag_list(data_dict={"vocabulary_id": CAPABILITY_VOCAB})
        return capability_tags
    except ObjectNotFound:
        return None
