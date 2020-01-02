"""
Class for wrapping the policy part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
import json
import logging


class Policy:

    """Class for wrapping the acl policies part of the vault api."""

    def __init__(self, vault):
        self.vault = vault

    def list(self):
        """ List all policies

        :returns: list of all policies

        """
        path = self.vault.normalize("/sys/policies/acl")
        address = self.vault.vault_adress + "/v1" + path
        request = self.vault.requests_request(
            "LIST", address, headers=self.vault.token_header
        )
        try:
            data = json.loads(request.content)["data"]["keys"]
        except json.decoder.JSONDecodeError:
            logging.exception("Listing the policy %s lead to the following error:", path)
            exit(1)
        return data


    def delete(self, policy_name):
        """ Delete the given policy permanently from vault

        :policy_name: name of the policy
        :returns: None

        """
        path = self.vault.normalize("/sys/policies/acl/" + policy_name)
        address = self.vault.vault_adress + "/v1" + path
        # Actually run vault
        logging.info("Deleting the policy: %s", address)
        self.vault.requests_request("DELETE", address, headers=self.vault.token_header)

    def add(self, policy_name, data):
        """ Add the given policy with the given data

        :policy_name: name of the new/updated policy
        :data: data of the policy as string
        :returns: None

        """
        path = self.vault.normalize("/sys/policies/acl/" + policy_name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Adding the policy: %s", address)
        payload = json.dumps({"policy": data})
        response = self.vault.requests_request(
            "POST", address, headers=self.vault.token_header, data=payload
        )
        if response.json()["data"]["version"] != 1:
            logging.warning("Policy already existed, creating new version with given data")

    def read(self, policy_name):
        """ read the details of the given policy

        :policy_name: name of the policy
        :returns: policy details as string

        """
        path = self.vault.normalize("/sys/policies/acl/" + policy_name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Reading the policy: %s", address)
        response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        policy_details = response.json()["data"]["policy"]
        return policy_details


def add(args, vault):
    """Run this module
    :returns: None

    """
    vault.policy.add(args.policy_name, json.loads(args.data))


def delete(args, vault):
    """Run this module
    :returns: None

    """
    vault.policy.delete(args.policy_name)


def list_policys(args, vault):
    """Run this module
    :returns: None

    """
    policy_list = vault.policy.list()
    for policy in policy_list:
        print(policy)


def read(args, vault):
    """Run this module
    :returns: None

    """
    policy_details = vault.policy.read(args.policy_name)
    print(policy_details)


def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    add_parser = subparsers.add_parser("policy-add")
    del_parser = subparsers.add_parser("policy-del")
    list_parser = subparsers.add_parser("policy-list")
    read_parser = subparsers.add_parser("policy-read")

    add_parser.set_defaults(func=add)
    del_parser.set_defaults(func=delete)
    list_parser.set_defaults(func=list_policys)
    read_parser.set_defaults(func=read)

    for parser in [add_parser, del_parser, read_parser]:
        parser.add_argument(
            "policy_name",
            help="name of the policy",
        )

    add_parser.add_argument("data", help="data of the policy as string")
