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

    users = vault.get_userpass_users()
    # TODO: add other users
    for user in users:
        print(user)


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("list_users")
    parser.set_defaults(func=run)
