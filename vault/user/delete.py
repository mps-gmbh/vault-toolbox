"""
This module adds a user, wrapps the password and returns a command with
which the password can be retrieved once.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
import logging

def run(args, vault):
    """Entrypoint when used as an executable
    :returns: None

    """
    user = vault.get_entity_by_name(args.user)
    if user is None:
        logging.error("The given user does not exist, %s%s",
                      "please choose one of the following users:\n\n",
                      "\n".join([entity["name"] for entity in vault.get_entities()]))
        exit(1)
    aliases = user["aliases"]
    for alias in aliases:
        logging.info("Deleting alias %s", alias["name"])
        vault.del_userpass_user(alias["name"])
    logging.info("Deleting entity %s", args.user)
    vault.del_entity(args.user)


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = subparsers.add_parser("user-del")
    parser.set_defaults(func=run)

    parser.add_argument("user", help="Vault user to delete")
