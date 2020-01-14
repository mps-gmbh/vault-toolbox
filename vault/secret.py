"""
Class for wrapping the secret part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.
"""
import json
import logging


class Secret:

    """Class for wrapping the secret part of the vault api."""

    def __init__(self, vault):
        self.vault = vault

    def list(self, engine_path, path):
        """ List secrets on a given path

        :engine_path: path of the secret engine
        :path: path to list
        :returns: list of the secrets

        """
        path = self.vault.normalize("/" + engine_path + "/metadata/" + path)
        address = self.vault.vault_adress + "/v1" + path
        request = self.vault.requests_request(
            "LIST", address, headers=self.vault.token_header
        )
        try:
            data = json.loads(request.content)["data"]["keys"]
        except json.decoder.JSONDecodeError:
            logging.exception("Listing the secret %s lead to the following error:", path)
            exit(1)
        return data

    def recursive_list(self, engine_path, path):
        """ List secrets on a given path recursively

        :engine_path: path of the secret engine
        :path: path to list
        :returns: generator for the secret list

        """
        secret_list = self.list(engine_path, path)
        for secret in secret_list:
            new_secret = self.vault.normalize(path + "/" + secret)
            yield new_secret
            if secret.endswith("/"):
                recursive_secrets = self.recursive_list(engine_path, new_secret)
                for recursive_secret in recursive_secrets:
                    yield recursive_secret

    def delete(self, engine_path, path):
        """ Delete the given secret permanently from vault

        :engine_path: path of the secret engine
        :path: path to delete
        :returns: None

        """
        path = self.vault.normalize("/" + engine_path + "/metadata/" + path)
        address = self.vault.vault_adress + "/v1" + path
        # Actually run vault
        logging.info("Deleting the secret: %s", address)
        self.vault.requests_request("DELETE", address, headers=self.vault.token_header)

    def add(self, engine_path, path, data):
        """ Add the given secret with the given data

        :engine_path: path of the secret engine
        :path: path of the new secret
        :data: data of the secret
        :returns: None

        """
        path = self.vault.normalize("/" + engine_path + "/data/" + path)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Adding the secret: %s", address)
        payload = json.dumps({"data": data})
        response = self.vault.requests_request(
            "POST", address, headers=self.vault.token_header, data=payload
        )
        if response.json()["data"]["version"] != 1:
            logging.warning("Secret already existed, creating new version with given data")

    def recursive_delete(self, engine_path, path):
        """ Delete all secrets under the given path permanently from vault

        :engine_path: path of the secret engine
        :path: path to delete
        :returns: None

        """

        for secret in self.recursive_list(engine_path, path):
            self.delete(engine_path, secret)

    def read(self, engine_path, path):
        """ read the details of the given secret

        :engine_path: path of the secret engine
        :path: path of the secret
        :returns: secret details as dict

        """
        path = self.vault.normalize("/" + engine_path + "/data/" + path)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Reading the secret: %s", address)
        response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        secret_details = response.json()["data"]["data"]
        return secret_details

    def recursive_mv(self, engine_path, from_path, to_path):
        """move the given folders with all secrets and versions

        :engine_path: path of the secret engine
        :from_path: path of the folders
        :to_path: path to move the folders
        :returns: None

        """
        if not from_path.endswith("/"):
            from_path = from_path + "/"

        if not to_path.endswith("/"):
            to_path = to_path + "/"

        for secret in self.recursive_list(engine_path, from_path):
            if secret.endswith("/"):
                continue
            new_secret_path = secret.replace(from_path, to_path)
            self.mv(engine_path, secret, new_secret_path)

    def mv(self, engine_path, from_path, to_path):
        """ move the given secret with all its versions

        :engine_path: path of the secret engine
        :from_path: path of the secret
        :to_path: path to move the secret to
        :returns: None

        """

        versions = self._read_version(engine_path, from_path)
        path = self.vault.normalize("/" + engine_path + "/data/" + from_path)
        for version in versions:
            address = self.vault.vault_adress + "/v1" + path + "?version={}".format(version)
            response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
            data = response.json()["data"]["data"]
            self.add(engine_path, to_path, data)
        self.delete(engine_path, from_path)

    def _read_version(self, engine_path, path):
        """ read the versions of the given secret

        :engine_path: path of the secret engine
        :path: path of the secret
        :returns: secret details as dict

        """
        path = self.vault.normalize("/" + engine_path + "/metadata/" + path)
        address = self.vault.vault_adress + "/v1" + path
        response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        return response.json()["data"]["versions"].keys()


def add(args, vault):
    """Run this module
    :returns: None

    """
    vault.secret.add(args.engine, args.vaultpath, json.loads(args.data))


def delete(args, vault):
    """Run this module
    :returns: None

    """
    if args.recursive:
        vault.secret.recursive_delete(args.engine, args.vaultpath)
        return
    vault.secret.delete(args.engine, args.vaultpath)


def list_secrets(args, vault):
    """Run this module
    :returns: None

    """
    secret_list = vault.secret.recursive_list(args.engine, args.vaultpath)
    for secret in secret_list:
        print(secret)


def read(args, vault):
    """Run this module
    :returns: None

    """
    secret_details = vault.secret.read(args.engine, args.vaultpath)
    print(secret_details)


def mv(args, vault):
    """Run this module
    :returns: None

    """
    if args.recursive:
        vault.secret.recursive_mv(args.engine, args.vaultpath, args.target_vaultpath)
        return
    vault.secret.mv(args.engine, args.vaultpath, args.target_vaultpath)


def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    add_parser = subparsers.add_parser("secret-add")
    del_parser = subparsers.add_parser("secret-del")
    list_parser = subparsers.add_parser("secret-list")
    read_parser = subparsers.add_parser("secret-read")
    mv_parser = subparsers.add_parser("secret-mv")

    add_parser.set_defaults(func=add)
    del_parser.set_defaults(func=delete)
    list_parser.set_defaults(func=list_secrets)
    read_parser.set_defaults(func=read)
    mv_parser.set_defaults(func=mv)

    for parser in [add_parser, del_parser, list_parser, read_parser, mv_parser]:
        if config is not None and "secret" in config and "engine" in config["secret"]:
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
            help="path of the secret inside the secret engine vault",
        )

    mv_parser.add_argument("target_vaultpath", help="path to move the secret to")

    add_parser.add_argument("data", help="data of the secret as json")

    for parser in [del_parser, mv_parser]:
        parser.add_argument(
            "-r", "--recursive", help="deletes secrets recursively", action="store_true"
        )
