from flask import Blueprint, abort
from property_api.app import app

import json
import os

properties = Blueprint('properties', __name__)

data_dir = app.root_path + "/data"


@properties.route("/<uprn>", methods=['GET'])
def get_property_summaries(uprn):
    property_info = lookup_property_info(uprn)

    summaries = []

    title_numbers = property_info['title_numbers']
    for title_number in title_numbers:
        if os.path.exists("{0}/{1}/{1}.json".format(data_dir, title_number)):
            reg_available = True
        else:
            reg_available = False

        deed_path = "{}/{}/deeds".format(data_dir, title_number)
        deeds = property_info['deed_ids']

        deed_types = []
        for deed in deeds:
            with open("{}/{}.json".format(deed_path, deed), mode='r', encoding='utf-8-sig') as f:
                deed_data = f.read()
            f.closed
            deed_types.append(
                {"id": deed, "deed_type": json.loads(deed_data)['deed_type']})

        title_summary = {
            "title_number": title_number,
            "register_available": reg_available,
            "deeds": deed_types,
            "con29_id": property_info["con29"]
        }
        summaries.append(title_summary)

    result = {
        "uprn": uprn,
        "address": property_info['address'],
        "details_held": summaries
    }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}


@properties.route("/<uprn>/landregisters", methods=["GET"])
def get_property_registers(uprn):
    property_info = lookup_property_info(uprn)

    details = []

    title_numbers = property_info['title_numbers']
    for title_number in title_numbers:
        with open("{0}/{1}/{1}.json".format(data_dir, title_number), mode='r', encoding='utf-8-sig') as f:
            read_data = f.read()
        f.closed
        details.append(json.loads(read_data))

    result = {
        "uprn": uprn,
        "address": property_info['address'],
        "landregisters": details
    }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}


@properties.route("/<uprn>/deeds", methods=["GET"])
def get_property_deeds(uprn):
    property_info = lookup_property_info(uprn)

    result_deeds = []

    title_numbers = property_info['title_numbers']
    for title_number in title_numbers:
        deed_path = "{}/{}/deeds".format(data_dir, title_number)
        deeds = property_info['deed_ids']

        deed_list = []

        for deed in deeds:
            with open("{}/{}.json".format(deed_path, deed), mode='r', encoding='utf-8-sig') as f:
                deed_data = f.read()
            f.closed
            deed_list.append(json.loads(deed_data))
        if deed_list:
            tn_deeds = {
                "title_number": title_number,
                "deeds": deed_list
            }
            result_deeds.append(tn_deeds)

    result = {
        "uprn": uprn,
        "address": property_info['address'],
        "deeds": result_deeds
    }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}


@properties.route("/<uprn>/deeds/<deed_id>", methods=["GET"])
def get_property_deed(uprn, deed_id):
    property_info = lookup_property_info(uprn)

    title_numbers = property_info['title_numbers']
    for title_number in title_numbers:
        deed_path = "{}/{}/deeds".format(data_dir, title_number)
        deeds = property_info['deed_ids']

        if int(deed_id) not in deeds:
            abort(404)

        if os.path.exists("{}/{}.json".format(deed_path, deed_id)):
            with open("{}/{}.json".format(deed_path, deed_id), mode='r', encoding='utf-8-sig') as f:
                deed_data = f.read()
            f.closed

            result = {
                "title_number": title_number,
                "deed": json.loads(deed_data),
                "uprn": uprn,
                "address": property_info['address']
            }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}


@properties.route("/<uprn>/con29", methods=["GET"])
def get_property_con29(uprn):
    property_info = lookup_property_info(uprn)

    if os.path.exists("{}/CON29/{}.json".format(data_dir, property_info["con29"])):
        with open("{}/CON29/{}.json".format(data_dir, property_info["con29"])) as f:
            con29_data = f.read()
        f.closed

    result = {
        "uprn": uprn,
        "address": property_info['address'],
        "con29": json.loads(con29_data)
    }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}


def lookup_property_info(uprn):
    with open("{}/properties.json".format(data_dir)) as lookup:
        lookup_data = lookup.read()
    lookup.closed

    lookup_data = json.loads(lookup_data)

    for property_info in lookup_data['properties']:
        if 'uprn' in property_info:
            if property_info['uprn'] == uprn:
                return property_info

    abort(404)
