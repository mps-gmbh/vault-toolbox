"""
This module adds a secret to vault

Author: Janosch Deurer

"""
def run(args, vault):
    """Run this module
    :returns: None

    """
    vault.secret.add(args.engine, args.vaultpath, args.data)


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = subparsers.add_parser("secret-add")
    parser.set_defaults(func=run)

    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument(
        "vaultpath",
        help="path where to delete the password inside the secret engine vault",
    )
    parser.add_argument("data", help="data of the secret as json")

    parser.add_argument(
        "-r", "--recursive", help="deletes secrets recursively", action="store_true"
    )
