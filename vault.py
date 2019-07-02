"""
Wrapper around the vault api. This has no claim to be a full representation of
the api but rather to provide convenience functions that are needed by MPS GmbH.
However, extensions are most welcome.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
import logging
import json
import random
import string
import os
import requests


class Vault:

    """Class for wrapping the vault http api. """

    def __init__(self, vault_adress, token):
        self.vault_adress = vault_adress
        self.token = token
        self.token_header = {"X-Vault-Token": self.token}

    def list(self, engine_path, path):
        """ List secrets on a given path

        :engine_path: path of the secret engine
        :path: path to list
        :returns: list of the secrets

        """
        path = _normalize("/" + engine_path + "/metadata/" + path)
        address = self.vault_adress + "/v1" + path
        # Actually run vault
        request = _requests_request("LIST", address, headers=self.token_header)
        data = json.loads(request.content)["data"]["keys"]
        return data

    def recursive_list(self, engine_path, path):
        """ List secrets on a given path recursively

        :engine_path: path of the secret engine
        :path: path to list
        :returns: generator for the secret list

        """
        secret_list = self.list(engine_path, path)
        for secret in secret_list:
            yield path + secret
            if secret.endswith("/"):
                recursive_secrets = self.recursive_list(engine_path, path + secret)
                for recursive_secret in recursive_secrets:
                    yield recursive_secret

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
        return self.vault_adress + _normalize(adress)

    def add_user(self, firstname, lastname, password=None):
        """ Add a userpass login, an entity and an alias to vault.
        The entity uses first and last name, the userpass only uses the second
        name, the alias connects both of the others.

        :firstname: Firstname of vault user to create
        :lastname: Lastname of vault user to create
        :password: If not provided a random one will be generated
        :returns: Password of the user

        """
        username = firstname.lower() + "." + lastname.lower()
        password = self._add_userpass_login(username, password)
        metadata = {
            "name": firstname + " " + lastname,
            "metadata": {"organization": "MPS GmbH"},
            "policies": ["base"],
        }
        entity_id = self._add_entity(metadata)
        self._add_alias(username, entity_id)
        return password

    def _add_userpass_login(self, username, password=None):
        """ Add a userpass login to vault

        :username: Userpass login name
        :password: If not provided a random one will be generated
        :returns: password

        """
        # If password is not given generate a random one
        if password is None:
            password = "".join(
                random.SystemRandom().choice(string.ascii_letters + string.digits)
                for _ in range(25)
            )
        # Add the user in vault
        address = self.vault_adress + "/v1/auth/userpass/users/" + username
        data = json.dumps({"password": password})
        logging.info("Creating userpass login for: %s", username)
        _requests_request("POST", address, headers=self.token_header, data=data)
        return password

    def get_userpass_users(self):
        """ Get all users
        :returns: Users

        """
        address = self.vault_adress + "/v1/auth/userpass/users"
        request = _requests_request("LIST", address, headers=self.token_header)
        return json.loads(request.content)["data"]["keys"]

    def del_userpass_user(self, user):
        """ Delete the given userpass user
        :returns: None

        """
        address = self.vault_adress + "/v1/auth/userpass/users/" + user
        request = requests.request("DELETE", address, headers=self.token_header)
        logging.debug("%s %s", request.status_code, request.reason)
        logging.debug(request.content)

    def _add_entity(self, data):
        """ Add entity to vault

        :data: Metadata that will be attached to the entity
        :returns: None

        """
        # Add the user in vault
        address = self.vault_adress + "/v1/identity/entity"
        payload = json.dumps(data)
        logging.info("Creating entity with data: %s ", data)
        request = _requests_request(
            "POST", address, headers=self.token_header, data=payload
        )
        return json.loads(request.content)["data"]["id"]

    def _add_alias(self, username, entity_id):
        """ Add an alias between the given userpass username and the given entity.

        :username: userpass username
        :entity_id: id of the entity for the alias

        """
        # Get mount accessor of userpass
        address = self.vault_adress + "/v1/sys/auth"
        request = _requests_request("GET", address, headers=self.token_header)
        userpass_accessor = json.loads(request.content)["userpass/"]["accessor"]

        # Add the user in vault
        address = self.vault_adress + "/v1/identity/entity-alias"
        payload = json.dumps(
            {
                "name": username,
                "canonical_id": entity_id,
                "mount_accessor": userpass_accessor,
            }
        )
        request = _requests_request(
            "POST", address, headers=self.token_header, data=payload
        )

    def wrap(self, data, ttl=600):
        """ Wrap the given data in vault
        :returns: wrapping token

        """
        address = self.vault_adress + "/v1/sys/wrapping/wrap"
        data = json.dumps(data)
        header = {"X-Vault-Wrap-TTL": str(ttl), **self.token_header}
        request = _requests_request("POST", address, headers=header, data=data)
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
        request = _requests_request("POST", address, headers=header)
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
        return "VAULT_ADDR=" + self.vault_adress + " ./vault_unwrap.py " + token


def _normalize(path):
    """Replace spaces with underscores, everything to lowercase, remove double
    slashes
    :path: path to be normalized
    :returns: normalized string

    """
    return path.replace(" ", "_").lower().replace("//", "/")


def _requests_request(*args, **kwargs):
    """ Overwrites the requests.requests method with a default argument for verify

    :returns: requests method

    """
    # key_path = os.path.abspath("lets-encrypt-x3-cross-signed.pem.txt")
    key_path = os.path.abspath("./ca_bundle.crt")
    kwargs["verify"] = key_path
    logging.debug(kwargs)
    logging.debug(args)
    request = requests.request(*args, **kwargs)
    logging.debug("%s %s", request.status_code, request.reason)
    logging.debug(request.content)
    return request
