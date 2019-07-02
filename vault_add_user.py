#!/usr/bin/python3
"""
This module adds a user, wrapps the password and returns a command with
which the password can be retrieved once.

Author: Janosch Deurer

"""
import logging
import argparse
import os

from init_logging import init_logging
from vault import Vault
from vault import unwrap_str


def main():
    """Entrypoint when used as an executable
    :returns: None

    """

    # Initialize Logging
    logging.basicConfig(level=logging.DEBUG)
    args = get_commandline_arguments()
    init_logging(args)

    vault = Vault(os.environ["VAULT_ADDR"], args.token)
    password = vault.add_user(args.firstname, args.lastname)
    token = vault.wrap({"password": password})
    unwrap = unwrap_str(token)
    print(unwrap)


def get_commandline_arguments():
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("token", help="Vault token")
    parser.add_argument("firstname", help="Firstname of vault user to create")
    parser.add_argument("lastname", help="Lastname of vault user to create")
    parser.add_argument("--logfile", help="path to a file the output is passed to")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="no output except errors", action="store_true"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
