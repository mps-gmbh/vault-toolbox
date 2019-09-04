"""
This module takes a given csv keypass export and imports it in vault.

Author: Janosch Deurer

"""
import logging
import csv
import json
import re
import os
import requests


def run(args, vault):
    """Run this module
    :returns: None

    """
    # TODO: fix too many local variables

    # Import data from csv
    csv_input = []
    with open(args.file, newline="") as csvfile:
        logging.info("Reading CSV file")
        csv_reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
        for row in csv_reader:
            logging.debug(row)
            csv_input.append(row)

    # Check whether all path start with a common path, this will then be
    # stipped
    logging.debug("Searching for a common leading path")
    leading_path = None
    for row in csv_input:
        if leading_path is None:
            leading_path = row["Group"]
        new_leading_path = ""
        for key, char in enumerate(leading_path):
            if not row["Group"][key] == char:
                break
            new_leading_path = new_leading_path + char
        leading_path = new_leading_path
    if leading_path:
        logging.info(
            "The common leading path %s was found and will be ignored", leading_path
        )

    for row in csv_input:
        # Strip the common leading path
        group = re.sub(r"^" + leading_path, "", row["Group"])
        # Remove spaces and double slashes
        path = normalize(
            "/"
            + args.engine
            + "/data/"
            + args.vaultpath
            + "/"
            + group
            + "/"
            + row["Title"]
        )
        del row["Group"]
        del row["Title"]
        # Delete empty rows
        new_row = dict()
        for field in row:
            if row[field]:
                new_row[field] = row[field]
        row = new_row
        address = os.environ["VAULT_ADDR"] + "/v1" + path
        logging.info("Creating new password")
        logging.info("Path: %s", address)
        data = json.dumps({"data": row})
        logging.debug("Data: %s", data)
        header = {"X-Vault-Token": os.environ["VAULT_DEV_ROOT_TOKEN_ID"]}
        logging.debug("Header: %s", header)
        if not args.dryrun:
            # Acually run vault
            request = requests.post(address, data=data, headers=header)
            logging.info("%s %s", request.status_code, request.reason)
            logging.debug(request.text)


def normalize(path):
    """Replace spaces with underscores, everything to lowercase, remove double
    slashes
    :returns: normalized string

    """
    return path.replace(" ", "_").lower().replace("//", "/")


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("import")
    parser.set_defaults(func=run)

    # TODO: merge the following two arguments
    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument(
        "vaultpath",
        help="path where to put the passwords inside the secret engine vault",
    )
    parser.add_argument("file", help="CSV file with keypass export")
    parser.add_argument(
        "--dryrun", "-d", help="Only show what would be executed", action="store_true"
    )
