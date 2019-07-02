#!/usr/bin/python3
"""
This module exports a given path in vault to html

Author: Janosch Deurer

"""
import logging
import argparse
import os

from init_logging import init_logging
from vault import Vault


def main():
    """Entrypoint when used as an executable
    :returns: None

    """

    # Initialize Logging
    logging.basicConfig(level=logging.DEBUG)
    args = get_commandline_arguments()
    init_logging(args)

    vault = Vault(os.environ["VAULT_ADDR"], args.token)
    secrets = vault.recursive_list(args.engine, args.vaultpath)
    path_depth = 0
    ul_count = 0
    for secret in secrets:
        new_path_depth = secret.count("/")
        if not secret.endswith("/"):
            new_path_depth = new_path_depth + 1
        if new_path_depth > path_depth:
            print("<ul>")
            ul_count = ul_count + 1
        if new_path_depth < path_depth:
            diff = path_depth - new_path_depth
            for _ in range(diff):
                print("</ul>")
            ul_count = ul_count - diff
        path_depth = new_path_depth
        ui_link = vault.path_to_ui_link(args.engine, secret)
        print(html_list_element(html_link(secret, ui_link)))
    for _ in range(ul_count):
        print("</ul>")


def html_link(text, url):
    """TODO: Docstring for html_link.
    :returns: TODO

    """
    return '<a href="' + url + '">' + text + "</a>"

def html_list_element(content):
    """TODO: Docstring for html_list_element.
    :returns: TODO

    """
    return "<li>" + content + "</li>"

def get_commandline_arguments():
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("token", help="Vault token")
    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument(
        "vaultpath",
        help="path where to put the passwords inside the secret engine vault",
    )
    parser.add_argument("--logfile", help="path to a file the output is passed to")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="no output except errors", action="store_true"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
