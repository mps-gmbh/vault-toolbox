"""
Class for wrapping the secret part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.

Author: Janosch Deurer
Mail: deurer@mps-med.de

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
        request = self.vault.requests_request("LIST", address, headers=self.vault.token_header)
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
        # Actually run vault
        logging.info("Adding the secret: %s", address)
        payload = '{"data": ' + data + '}'
        response = self.vault.requests_request("POST", address, headers=self.vault.token_header,
                                               data=payload)
        if response.json()["data"]["version"] != 1:
            logging.info("Secret already existed, creating new version with given data")


    def recursive_delete(self, engine_path, path):
        """ Delete all secrets under the given path permanently from vault

        :engine_path: path of the secret engine
        :path: path to delete
        :returns: None

        """
        for secret in self.recursive_list(engine_path, path):
            self.delete(engine_path, secret)
