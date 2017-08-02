from flask import Blueprint, abort
from property_api.app import app

import glob
import json
import os

properties = Blueprint('properties', __name__)

data_dir = app.root_path + "/data"

@properties.route("/<uprn>", methods=['GET'])
def get_property_summaries(uprn):
    with open("{}/uprns.json".format(data_dir)) as lookup:
        lookup_data = lookup.read()
    lookup.closed

    lookup_data = json.loads(lookup_data)

    if uprn in lookup_data:
        title_numbers = lookup_data[uprn]
    else:
        abort(404)

    summaries = []

    for title_number in title_numbers:
        if os.path.exists("{0}/{1}/{1}.json".format(data_dir, title_number)):
            reg_available = True
        else:
            reg_available = False

        deed_path = "{}/{}/deeds".format(data_dir, title_number)
        deeds = [deed for deed in glob.glob(deed_path + '/*.json')]

        if not deeds:
            abort(404)

        deed_types = []

        for deed in deeds:
            with open(deed) as f2:
                deed_data = f2.read()
            f2.closed
            deed_types.append(json.loads(deed_data)['deed_type'])

        title_summary = {
            "title_number": title_number,
            "register_available": reg_available,
            "deeds": deed_types
        }

        summaries.append(title_summary)

    result = {
        "uprn": uprn,
        "details_held": summaries
    }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}


@properties.route("/<uprn>/landregisters", methods=["GET"])
def get_property_registers(uprn):
    with open("{}/uprns.json".format(data_dir)) as lookup:
        lookup_data = lookup.read()
    lookup.closed

    lookup_data = json.loads(lookup_data)

    if uprn in lookup_data:
        title_numbers = lookup_data[uprn]
    else:
        abort(404)

    details = []

    for title_number in title_numbers:
        with open("{0}/{1}/{1}.json".format(data_dir, title_number)) as f:
            read_data = f.read()
        f.closed
        details.append(json.loads(read_data))

    if not details:
        abort(404)

    result = {
        "uprn": uprn,
        "landregisters": details
    }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}


@properties.route("/<uprn>/deeds", methods=["GET"])
def get_property_deeds(uprn):
    with open("{}/uprns.json".format(data_dir)) as lookup:
        lookup_data = lookup.read()
    lookup.closed

    lookup_data = json.loads(lookup_data)

    if uprn in lookup_data:
        title_numbers = lookup_data[uprn]
    else:
        abort(404)

    deeds = []

    for title_number in title_numbers:
        deed_path = "{}/{}/deeds".format(data_dir, title_number)
        deeds = [deed for deed in glob.glob(deed_path + '/*.json')]

        if not deeds:
            abort(404)

        deed_results = []

        for deed in deeds:
            with open(deed) as f2:
                deed_data = f2.read()
            f2.closed
            deed_results.append(json.loads(deed_data))
        if deed_results:
            tn_deeds = {
                "title_number": title_number,
                "deeds": deed_results
            }
            deeds.append(tn_deeds)

    if not deeds:
        abort(404)

    result = {
        "uprn": uprn,
        "deeds": deeds
    }

    return json.dumps(result, sort_keys=True, separators=(',', ':')), 200, {"Content-Type": "application/json"}