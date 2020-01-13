"""
Class for wrapping the policy part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.
"""
import json
import logging
import os


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

    def read(self, policy_name):
        """ read the details of the given policy

        :policy_name: name of the policy
        :returns: policy details as string

        """
        path = self.vault.normalize("/sys/policies/acl/" + policy_name)
        address = self.vault.vault_adress + "/v1" + path
        logging.debug("Reading the policy: %s", address)
        response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        policy_details = response.json()["data"]["policy"]
        return policy_details


def add(args, vault):
    """Run this module
    :returns: None

    """
    with open(args.datafile, 'r') as f:
        data = f.read()
        vault.policy.add(args.policy_name, data)


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


def export(args, vault):
    """Run this module
    :returns: None

    """
    for policy in vault.policy.list():
        policy_details = vault.policy.read(policy)
        if not os.path.isdir(args.dir):
            os.mkdir(args.dir)
        policy_file = os.path.join(args.dir, policy + ".hcl")
        with open(policy_file, 'w') as f:
            f.write(policy_details)


def policy_import(args, vault):
    """Run this module
    :returns: None

    """
    for policy_file in os.listdir(args.dir):
        if not policy_file.endswith(".hcl"):
            continue
        filepath = os.path.join(args.dir, policy_file)
        with open(filepath, 'r') as f:
            policy_details = f.read()
        # Ignore empty policies
        if not policy_details:
            continue
        # Remove file extension to generate policy name
        policy_name = os.path.splitext(policy_file)[0]
        vault.policy.add(policy_name, policy_details)

    delete_policies = []
    for policy in vault.policy.list():
        if policy + ".hcl" not in os.listdir(args.dir):
            delete_policies.append(policy)

    if delete_policies:
        print("The following policies will be DELETED:")
        for policy in delete_policies:
            print(policy)
        user_input = input("If you want to continue type yes: ")
        if user_input != "yes":
            print("Aborting deletion")
            return
        for policy in delete_policies:
            vault.policy.delete(policy)




def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    add_parser = subparsers.add_parser("policy-add")
    del_parser = subparsers.add_parser("policy-del")
    list_parser = subparsers.add_parser("policy-list")
    read_parser = subparsers.add_parser("policy-read")
    export_parser = subparsers.add_parser("policy-export")
    import_parser = subparsers.add_parser("policy-import")

    add_parser.set_defaults(func=add)
    del_parser.set_defaults(func=delete)
    list_parser.set_defaults(func=list_policys)
    read_parser.set_defaults(func=read)
    export_parser.set_defaults(func=export)
    import_parser.set_defaults(func=policy_import)

    for parser in [add_parser, del_parser, read_parser]:
        parser.add_argument(
            "policy_name",
            help="name of the policy",
        )

    add_parser.add_argument("datafile", help="filename containing policy data")
    for parser in [import_parser, export_parser]:
        parser.add_argument("dir", help="directory for the policies")
