"""
This module adds a user, wrapps the password and returns a curl command with
which the password can be retrieved once.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
def run(args, vault):
    """Run this module

    :args: Commandline arguments
    :returns: None

    """
    print(vault.unwrap())

def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("unwrap")
    parser.set_defaults(func=run)
