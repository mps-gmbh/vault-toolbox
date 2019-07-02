#!/usr/bin/python3
"""
This module takes a given csv keypass export and imports it in vault.

Author: Janosch Deurer

"""
import logging
import argparse
import csv
import json
import re
import os
import requests


def main():
    """Entrypoint when used as an executable
    :returns: None

    """

    # Initialize Logging
    logging.basicConfig(level=logging.DEBUG)
    args = get_commandline_arguments()
    initialize_logging(args)

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


def get_commandline_arguments():
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument(
        "vaultpath",
        help="path where to put the passwords inside the secret engine vault",
    )
    parser.add_argument("file", help="CSV file with keypass export")
    parser.add_argument("--logfile", help="path to a file the output is passed to")
    parser.add_argument(
        "--dryrun", "-d", help="Only show what would be executed", action="store_true"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="no output except errors", action="store_true"
    )
    args = parser.parse_args()
    return args


def initialize_logging(commandline_args):
    """Initialize logging as given in the commandline arguments

    :commandline_args: namespace with commandline arguments including verbosity
    and logfile if given
    :returns: None

    """
    loglevel = "INFO"
    if commandline_args.verbosity:
        loglevel = "DEBUG"
    if commandline_args.quiet:
        loglevel = "ERROR"

    logfile = commandline_args.logfile

    # If logfile is given, generate a new logger with file handling
    if logfile:
        filehandler = logging.FileHandler(logfile, "a")
        formatter = logging.Formatter()
        filehandler.setFormatter(formatter)
        logger = logging.getLogger()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger.addHandler(filehandler)

    loglevel = getattr(logging, loglevel.upper())
    logging.getLogger().setLevel(loglevel)


if __name__ == "__main__":
    main()
