from flask import Blueprint, abort
from property_api.app import app

import glob
import json

properties = Blueprint('properties', __name__)

@properties.route("/<uprn>/landregister", methods=["GET"])
def get_properties(uprn):
    data_dir = app.root_path + "/data"
    files = [file for file in glob.glob(data_dir + '/**/*.json')]
    if not files:
        abort(404)

    results = []

    for file in files:
        with open(file) as f:
            read_data = f.read()
        f.closed
        details = json.loads(read_data)
        if 'lr_uprns' in details and int(uprn) in details['lr_uprns']:
            results.append(details)

    if not results:
        abort(404)

    return json.dumps(results), 200, {"Content-Type": "application/json"}


@properties.route("/<uprn>/deeds", methods=["GET"])
def get_property_deeds(uprn):
    data_dir = app.root_path + "/data"
    files = [file for file in glob.glob(data_dir + '/**/*.json')]
    if not files:
        abort(404)

    results = []

    for file in files:
        with open(file) as f:
            read_data = f.read()
        f.closed
        details = json.loads(read_data)
        if 'lr_uprns' in details and int(uprn) in details['lr_uprns']:
            deed_results = []
            title_number = details['title_number']
            # TODO(Aron) use TN to get path and load/return docs
            deed_path = "{}/{}/deeds".format(data_dir, title_number)
            deeds = [deed for deed in glob.glob(deed_path + '/*.json')]
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
                results.append(tn_deeds)

    if not results:
        abort(404)

    return json.dumps(results), 200, {"Content-Type": "application/json"}