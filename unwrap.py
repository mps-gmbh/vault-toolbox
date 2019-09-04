"""
This module adds a user, wrapps the password and returns a curl command with
which the password can be retrieved once.

Author: Janosch Deurer

"""
import os

from vault import Vault


def run(args):
    """Run this module

    :args: Commandline arguments
    :returns: None

    """
    vault = Vault(os.environ["VAULT_ADDR"], args.token)
    print(vault.unwrap())

def get_commandline_parser(subparsers):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("unwrap")
    parser.set_defaults(func=run)
