"""
Class for wrapping the totp part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
import json
import logging

class Totp:

    """Class for wrapping the secret part of the vault api."""

    def __init__(self, vault):
        self.vault = vault


    def list(self, engine_path):
        """ List secrets on a given path

        :engine_path: path of the secret engine
        :returns: list of the secrets

        """
        path = self.vault.normalize("/" + engine_path + "/keys")
        # TODO: replace with urlparse everywhere
        address = self.vault.vault_adress + "/v1" + path
        request = self.vault.requests_request("LIST", address, headers=self.vault.token_header)
        data = json.loads(request.content)["data"]["keys"]
        return data


    def delete(self, engine_path, name):
        """ Delete the given totp permanently from vault

        :engine_path: path of the secret engine
        :name: name of the totp to delete
        :returns: None

        """
        path = self.vault.normalize("/" + engine_path + "/keys/" + name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Deleting the totp key: %s", address)
        self.vault.requests_request("DELETE", address, headers=self.vault.token_header)

    def add(self, engine_path, name, issuer, account):
        """ Add the given totp key

        :engine_path: path of the secret engine
        :name: path of the new secret
        :data: data of the secret
        :returns: None

        """
        path = self.vault.normalize("/" + engine_path + "/keys/" + name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Adding the totp key: %s", address)
        payload_dict = dict()
        payload_dict["generate"] = True
        payload_dict["exported"] = False
        payload_dict["issuer"] = issuer
        payload_dict["account_name"] = account
        payload = json.dumps(payload_dict)
        self.vault.requests_request("POST", address, headers=self.vault.token_header,
                                    data=payload)

    def read(self, engine_path, name):
        """ Read a value from the given totp key

        :engine_path: path of the secret engine
        :name: name of the totp key
        :returns: time based token

        """
        path = self.vault.normalize("/" + engine_path + "/code/" + name)
        address = self.vault.vault_adress + "/v1" + path
        response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        data = json.loads(response.content)["data"]["code"]
        return data

    def add_from_url(self, engine_path, name, totp_url):
        """Add totp from a given url

        :engine: totp engine
        :name: totp token name
        :totp_url: url with the details of the token
        :returns: None

        """
        path = self.vault.normalize("/" + engine_path + "/keys/" + name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Adding the totp key: %s", address)
        payload_dict = dict()
        payload_dict["generate"] = False
        payload_dict["url"] = totp_url
        payload = json.dumps(payload_dict)
        self.vault.requests_request("POST", address, headers=self.vault.token_header,
                                    data=payload)


def add(args, vault):
    """Run add operation
    :args: Parsed commandline arguments
    :vault: Vault class
    :returns: None

    """
    vault.totp.add(args.engine, args.name, args.issuer, args.account)

def list_totp(args, vault):
    """Run list operation

    :args: Parsed commandline arguments
    :vault: Vault class
    :returns: None

    """
    keys = vault.totp.list(args.engine)
    print("## Totp Keys:\n")
    for key in keys:
        print(key)

def read(args, vault):
    """Run read operation

    :args: Parsed commandline arguments
    :vault: Vault class
    :returns: None

    """
    key = vault.totp.read(args.engine, args.name)
    print("## Value for secret " + args.name)
    print(key)

def delete(args, vault):
    """Run delete operation

    :args: Parsed commandline arguments
    :vault: Vault class
    :returns: None

    """
    vault.totp.delete(args.engine, args.name)

def totp_import(args, vault):
    """Run import operation

    :args: Parsed commandline arguments
    :vault: Vault class
    :returns: None

    """
    vault.totp.add_from_url(args.engine, args.name, args.url)


def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    add_parser = subparsers.add_parser("totp-add")
    list_parser = subparsers.add_parser("totp-list")
    read_parser = subparsers.add_parser("totp-read")
    del_parser = subparsers.add_parser("totp-del")
    import_parser = subparsers.add_parser("totp-import")


    add_parser.set_defaults(func=add)
    list_parser.set_defaults(func=list_totp)
    read_parser.set_defaults(func=read)
    del_parser.set_defaults(func=delete)
    import_parser.set_defaults(func=totp_import)

    for parser in [add_parser, list_parser, read_parser, del_parser, import_parser]:
        if config is not None and "totp" in config and "engine" in config["totp"]:
            parser.add_argument(
                "engine",
                nargs="?",
                default=config["totp"]["engine"],
                help="path of the secret engine in vault, if "
                + "not provided the path in the config will be "
                + "used",
            )
        else:
            parser.add_argument("engine", help="path of the secret engine in vault")

    for parser in [add_parser, read_parser, del_parser, import_parser]:
        parser.add_argument("name", help="name of the totp key")

    add_parser.add_argument("issuer", help="name of the issuer")
    add_parser.add_argument("account", help="account of this key")

    import_parser.add_argument("url", help="TOTP url")
