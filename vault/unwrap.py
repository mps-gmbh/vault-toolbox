"""
This module adds a user, wrapps the password and returns a curl command with
which the password can be retrieved once.
"""


def run(_, vault):
    """Run this module

    :args: Commandline arguments
    :returns: None

    """
    print(vault.unwrap())


def parse_commandline_arguments(subparsers, _):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("unwrap")
    parser.set_defaults(func=run)
