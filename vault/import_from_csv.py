"""
This module takes a given csv keypass export and imports it in vault.
"""
import logging
import csv
import re


def run(args, vault):
    """Run this module
    :returns: None

    """
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
        path = normalize(args.vaultpath + "/" + group + "/" + row["Title"])
        del row["Group"]
        del row["Title"]
        # Delete empty rows
        new_row = dict()
        for field in row:
            if row[field]:
                new_row[field] = row[field]
        row = new_row
        if not args.dryrun:
            # Acually run vault
            vault.secret.add(args.engine, path, row)


def normalize(path):
    """Replace spaces with underscores, everything to lowercase, remove double
    slashes
    :returns: normalized string

    """
    return path.replace(" ", "_").lower().replace("//", "/")


def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("import_from_csv")
    parser.set_defaults(func=run)

    # TODO: Fix this code duplication
    if config is not None and "secret" in config and "engine" in config["secret"]:
        parser.add_argument(
            "engine",
            nargs="?",
            default=config["secret"]["engine"],
            help="path of the secret engine in vault, if "
            + "not provided the path in the config will be "
            + "used",
        )
    else:
        parser.add_argument("engine", help="path of the secret engine in vault")

    parser.add_argument(
        "vaultpath",
        help="path where to put the passwords inside the secret engine vault",
    )
    parser.add_argument("file", help="CSV file with keypass export")
    parser.add_argument(
        "--dryrun", "-d", help="Only show what would be executed", action="store_true"
    )
