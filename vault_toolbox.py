#!/usr/bin/python3
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

import init_logging
import unwrap
import export_to_html
import list_users
import add_user
import del_user
import del_secret
import vault_import
from vault import Vault


def main():
    """Entrypoint when used as an executable
    :returns: None

    """
    # Initialize Logging
    logging.basicConfig(level=logging.DEBUG)
    args = get_commandline_arguments()
    init_logging.init_logging(args)
    vault = Vault(os.environ["VAULT_ADDR"], args.token)
    args.func(args, vault)




def get_commandline_arguments():
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
    subparsers = parser.add_subparsers(help="subcommand", dest='subcommand', required=True)

    for subcommand in [unwrap, export_to_html, list_users,
                       add_user, del_user, del_secret, vault_import]:
        subcommand.parse_commandline_arguments(subparsers)

    for _, subparser in subparsers.choices.items():
        subparser.add_argument("token", help="Vault token")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
