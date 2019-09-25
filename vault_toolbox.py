#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK
"""
Commanline interface for the vault toolbox.

Wrapper around the vault api. This has no claim to be a full representation of
the api but rather to provide convenience functions that are needed by MPS GmbH.
However, extensions are most welcome.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
import logging
import argparse
import os
import argcomplete
import yaml

import vault.unwrap
import vault.export_to_html
import vault.user
import vault.secret
import vault.totp
import vault.import_from_csv
from vault.vault import Vault


def main():
    """Entrypoint when used as an executable
    :returns: None

    """
    # Initialize Logging
    logging.basicConfig(level=logging.DEBUG)

    config = read_config()
    args = get_commandline_arguments(config)
    init_logging(args)
    # TODO: Read url from file or cli
    args.func(args, Vault(os.environ["VAULT_ADDR"], args.token))


def get_commandline_arguments(config):
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", help="path to a file the output is passed to")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="no output except errors", action="store_true"
    )
    # Add parsers for subcommand
    subparsers = parser.add_subparsers(
        help="subcommand", dest="subcommand", required=True
    )

    for subcommand in [
            vault.secret,
            vault.user,
            vault.totp,
            vault.unwrap,
            vault.export_to_html,
            vault.import_from_csv,
    ]:
        subcommand.parse_commandline_arguments(subparsers)

    for _, subparser in subparsers.choices.items():
        if config["token"]:
            subparser.add_argument("token", nargs='?', default=config["token"],
                                   help="Vault token, if not provided, " + \
                                   "the token from the config will be used")
        else:
            subparser.add_argument("token", help="Vault token")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    return args


def init_logging(commandline_args):
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

def read_config():
    """Parses config and returns config values
    :returns: config as dict
    """
    try:
        stream = open("config.yaml", "r")
    except FileNotFoundError:
        return None
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exception:
        logging.error("YAML error while parsing config.yaml:\n%s", exception)
        exit()
    return config

if __name__ == "__main__":
    main()
