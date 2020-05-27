"""
Wrapper around the vault api. This has no claim to be a full representation of
the api but rather to provide convenience functions that are needed by MPS GmbH.
However, extensions are most welcome.
"""
import logging
import json
import os
import requests
from .secret import Secret
from .totp import Totp
from .user import User
from .policy import Policy
from .group import Group


class Vault:

    """Class for wrapping the vault http api. """

    def __init__(self, vault_adress, token):
        self.vault_adress = vault_adress
        self.token = token
        self.token_header = {"X-Vault-Token": self.token}

        # Initialize Subclasses
        self.secret = Secret(self)
        self.totp = Totp(self)
        self.user = User(self)
        self.policy = Policy(self)
        self.group = Group(self)

    def path_to_ui_link(self, engine_path, path):
        """ Generate a url from the given path

        :engine_path: path of the secret engine
        :path: path of the secret
        :returns: url to get the path or secret in the ui

        """
        if path.endswith("/"):
            path_extension = "/list/"
        else:
            path_extension = "/show/"

        adress = "/ui/vault/secrets/" + engine_path + path_extension + path
        return self.vault_adress + self.normalize(adress)

    def wrap(self, data, ttl=600):
        """ Wrap the given data in vault
        :returns: wrapping token

        """
        address = self.vault_adress + "/v1/sys/wrapping/wrap"
        data = json.dumps(data)
        header = {"X-Vault-Wrap-TTL": str(ttl), **self.token_header}
        request = self.requests_request("POST", address, headers=header, data=data)
        return json.loads(request.content)["wrap_info"]["token"]

    def unwrap(self, token=None):
        """ Unwrap the given token
        :token: token to unwrap if not given the class token is used
        :returns: Unwraped data

        """
        if token is None:
            token = self.token
        header = {"X-Vault-Token": token}
        address = self.vault_adress + "/v1/sys/wrapping/unwrap"
        request = self.requests_request("POST", address, headers=header)
        try:
            data = json.loads(request.content)["data"]
        except KeyError:
            data = json.loads(request.content)["errors"][0]

        return data

    def unwrap_str(self, token):
        """ Generates an unwrap commanline that can be used to unwrap the token.
        :token: token to unwrap
        :returns: unwrap commandline
        """
        return "VAULT_ADDR=" + self.vault_adress + " ./vault_toolbox.py unwrap " + token

    @staticmethod
    def normalize(path):
        """Replace spaces with underscores, remove double
        slashes
        :path: path to be normalized
        :returns: normalized string

        """
        # TODO: fix this
        return path.replace(" ", "%20").replace("//", "/")

    @staticmethod
    def requests_request(*args, **kwargs):
        """ Overwrites the requests.requests method with a default argument for verify

        :returns: requests method

        """
        key_path = os.path.abspath("./vault/ca_bundle.crt")
        kwargs["verify"] = key_path
        logging.debug(kwargs)
        logging.debug(args)
        try:
            response = requests.request(*args, **kwargs)
        except Exception as error:
            logging.error(
                "An error occured during the connection to vault:\n\n %s \n", error
            )
            exit(1)
        logging.debug("%s %s", response.status_code, response.reason)
        logging.debug(response.content)
        if response.status_code > 399:
            logging.error("%s %s", response.status_code, response.reason)
            error_text = "\n".join(response.json()["errors"])
            if error_text:
                logging.error(error_text)
            exit(1)
        return response
