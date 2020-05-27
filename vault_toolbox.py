#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK
"""
Commanline interface for the vault toolbox.

Wrapper around the vault api. This has no claim to be a full representation of
the api but rather to provide convenience functions that are needed by MPS GmbH.
However, extensions are most welcome.
"""
import logging
import argparse
import yaml

try:
    import argcomplete
except ImportError:
    pass
import vault.unwrap
import vault.export_to_html
import vault.user
import vault.secret
import vault.totp
import vault.policy
import vault.group
import vault.import_from_csv
from vault.vault import Vault


def main():
    """Entrypoint when used as an executable
    :returns: None

    """
    # Initialize Logging
    logging.basicConfig(level=logging.DEBUG)

    config = read_config()
    args = get_commandline_arguments(config)
    init_logging(args)
    try:
        args.func(args, Vault(args.url, args.token))
    except AttributeError:
        print(args.help)


def get_commandline_arguments(config):
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
    subparsers = parser.add_subparsers(help="subcommand", dest="subcommand")

    for subcommand in [
        vault.secret,
        vault.user,
        vault.totp,
        vault.unwrap,
        vault.export_to_html,
        vault.import_from_csv,
        vault.policy,
        vault.group,
    ]:
        subcommand.parse_commandline_arguments(subparsers, config)

    for _, subparser in subparsers.choices.items():
        if config is not None and "token" in config:
            subparser.add_argument(
                "token",
                nargs="?",
                default=config["token"],
                help="Vault token, if not provided, "
                + "the token from the config will be used",
            )
        else:
            subparser.add_argument("token", help="Vault token")

        if config is not None and "url" in config:
            subparser.add_argument(
                "url",
                nargs="?",
                default=config["url"],
                help="Url of vault server, if not provided, "
                + "the url from the config will be used",
            )
        else:
            subparser.add_argument("url", help="Url of vault server")

    if "argcomplete" in globals():
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    return args


def init_logging(commandline_args):
    """Initialize logging as given in the commandline arguments

    :commandline_args: namespace with commandline arguments including verbosity
    and logfile if given
    :returns: None

    """
    loglevel = "INFO"
    if commandline_args.verbosity:
        loglevel = "DEBUG"
    if commandline_args.quiet:
        loglevel = "ERROR"

    logfile = commandline_args.logfile

    # If logfile is given, generate a new logger with file handling
    if logfile:
        filehandler = logging.FileHandler(logfile, "a")
        formatter = logging.Formatter()
        filehandler.setFormatter(formatter)
        logger = logging.getLogger()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger.addHandler(filehandler)

    loglevel = getattr(logging, loglevel.upper())
    logging.getLogger().setLevel(loglevel)


def read_config():
    """Parses config and returns config values
    :returns: config as dict
    """
    try:
        stream = open("config.yaml", "r")
    except FileNotFoundError:
        return None
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exception:
        logging.error("YAML error while parsing config.yaml:\n%s", exception)
        exit()
    # Remove / on the end of url
    if "url" in config:
        config["url"] = config["url"].rstrip("/")

    return config


if __name__ == "__main__":
    main()
