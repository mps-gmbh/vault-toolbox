#!/usr/bin/python3
"""
doc
"""
import logging
import argparse

import init_logging
import unwrap


def main():
    """Entrypoint when used as an executable
    :returns: None

    """
    # Initialize Logging
    logging.basicConfig(level=logging.DEBUG)
    args = get_commandline_arguments()
    init_logging.init_logging(args)
    args.func(args)




def get_commandline_arguments():
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", help="path to a file the output is passed to")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="no output except errors", action="store_true"
    )
    # Add parsers for subcommand
    subparsers = parser.add_subparsers(help="subcommand", dest='subcommand', required=True)
    unwrap.get_commandline_parser(subparsers)

    parser.add_argument("token", help="Vault token")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
