"""
This module adds a user, wrapps the password and returns a command with
which the password can be retrieved once.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
def run(_, vault):
    """Entrypoint when used as an executable
    :returns: None

    """

    users = vault.get_userpass_users()
    print("## Userpass users:\n")
    for user in users:
        print(user)


    print("\n## Entities:\n")
    users = vault.get_entities()
    for user in users:
        print(user["name"])

    print("\n## Entity aliases:\n")
    users = vault.get_entities()
    for user in users:
        print(user["name"] + " -> aliases:" + str([alias["name"] for alias in user["aliases"]]))



def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("list_users")
    parser.set_defaults(func=run)
