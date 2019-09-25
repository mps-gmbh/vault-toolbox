"""
This module exports a given path in vault to html

Author: Janosch Deurer

"""
def run(args, vault):
    """Run this module
    :returns: None

    """

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
    """Creates an html link element from the given text and url
    :returns: html link element as string

    """
    return '<a href="' + url + '">' + text + "</a>"

def html_list_element(content):
    """Creates an html list element from the given content
    :returns: html list element as string

    """
    return "<li>" + content + "</li>"

def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    parser = subparsers.add_parser("export")
    parser.set_defaults(func=run)
    # TODO: Fix code duplication
    if "secret" in config and "engine" in config["secret"]:
        parser.add_argument(
            "engine",
            nargs="?",
            default=config["secret"]["engine"],
            help="path of the secret engine in vault, if "
            + "not provided the path in the config will be "
            + "used",
        )
    else:
        parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument(
        "vaultpath",
        help="path where to find the passwords inside the secret engine vault",
    )
