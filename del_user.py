"""
This module adds a user, wrapps the password and returns a command with
which the password can be retrieved once.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
def run(args, vault):
    """Entrypoint when used as an executable
    :returns: None

    """
    vault.del_userpass_user(args.user)
    # TODO: delete other usertypes


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = subparsers.add_parser("del_user")
    parser.set_defaults(func=run)

    parser.add_argument("user", help="Vault user to delete")
