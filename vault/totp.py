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


def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    # TODO: Fix code duplication of engine and name
    parser = subparsers.add_parser("totp-add")
    parser.set_defaults(func=add)

    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument("name", help="name of the totp key")
    parser.add_argument("issuer", help="name of the issuer")
    parser.add_argument("account", help="account of this key")

    parser = subparsers.add_parser("totp-list")
    parser.set_defaults(func=list_totp)

    parser.add_argument("engine", help="path of the secret engine in vault")

    parser = subparsers.add_parser("totp-read")
    parser.set_defaults(func=read)

    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument("name", help="name of the totp key")

    parser = subparsers.add_parser("totp-del")
    parser.set_defaults(func=delete)

    parser.add_argument("engine", help="path of the secret engine in vault")
    parser.add_argument("name", help="name of the totp key")
