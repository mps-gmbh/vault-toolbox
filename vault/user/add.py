"""
This module adds a user, wrapps the password and returns a command with
which the password can be retrieved once.

Author: Janosch Deurer

"""
def run(args, vault):
    """Entrypoint when used as an executable
    :returns: None

    """
    password = vault.add_user(args.firstname, args.lastname)
    token = vault.wrap({"password": password})
    unwrap = vault.unwrap_str(token)
    print(unwrap)


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("user-add")
    parser.set_defaults(func=run)

    parser.add_argument("firstname", help="Firstname of vault user to create")
    parser.add_argument("lastname", help="Lastname of vault user to create")
