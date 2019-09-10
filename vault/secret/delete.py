"""
This deletes a secret from vault

Author: Janosch Deurer

"""
def run(args, vault):
    """Run this module
    :returns: None

    """
    # TODO: Add error if deletion was not successfull
    if args.recursive:
        vault.secret.recursive_delete(args.engine, args.vaultpath)
        return
    vault.secret.delete(args.engine, args.vaultpath)


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    # TODO: make more secret based commands
    parser = subparsers.add_parser("secret-del")
    parser.set_defaults(func=run)

    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument(
        "vaultpath",
        help="path where to delete the password inside the secret engine vault",
    )
    parser.add_argument(
        "-r", "--recursive", help="deletes secrets recursively", action="store_true"
    )
