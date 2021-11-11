from ckan.plugins.toolkit import get_action, ObjectNotFound


user = get_action("get_site_user")({"ignore_auth": True}, {})
context = {"user": user["name"]}

CAPABILITY_VOCAB = u"capabilities"
STATUS_VOCAB = u"standard_status"

import logging

logging.basicConfig(level=logging.INFO)

# TODO:
# Status
#


def _get_tag_list(vocab_name):
    try:
        tag_list = get_action("tag_list")
        tags = tag_list(data_dict={"vocabulary_id": vocab_name})
        return tags
    except ObjectNotFound:
        return None


# TODO: the various tag generators can probably be accomplished in a loop/func
def _create_status_tags():
    status_tags = [
        u"ACTIVE",
        u"DRAFT",
        u"DEPRECATED",
        u"RETIRED",
    ]
    # tag_list = get_action("tag_list")
    # tags = tag_list(data_dict={"vocabulary_id": STATUS_VOCAB})
    # if len(tags) < 1:
    #     for tag in status_tags:
    #         data = {
    #             "name": tag,
    #             "vocabulary_id": STATUS_VOCAB,
    #         }
    #         get_action("tag_create")(context, data)

    try:
        data = {"id": STATUS_VOCAB}
        get_action("vocabulary_show")(context, data)
    except ObjectNotFound:
        vocab = get_action("vocabulary_create")(context, data)
        for tag in status_tags:
            data = {
                "name": tag,
                "vocabulary_id": vocab["id"],
            }
            get_action("tag_create")(context, data)


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

    try:
        data = {"id": CAPABILITY_VOCAB}
        get_action("vocabulary_show")(context, data)
    except ObjectNotFound:
        data = {"name": "capabilities"}
        vocab = get_action("vocabulary_create")(context, data)
        for tag in capability_tags:
            data = {"name": tag, "vocabulary_id": vocab["id"]}
            get_action("tag_create")(context, data)


def statuses():
    _create_status_tags()
    return _get_tag_list(STATUS_VOCAB)


def capabilities():
    _create_capabilities_tags()
    return _get_tag_list(CAPABILITY_VOCAB)
