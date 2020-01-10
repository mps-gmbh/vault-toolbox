"""
Class for wrapping the group part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.
"""
import json
import logging


class Group:

    """Class for wrapping the group part of the vault api."""

    def __init__(self, vault):
        self.vault = vault

    def list(self):
        """ List all groups

        :returns: list of all groups

        """
        path = self.vault.normalize("/identity/group/name")
        address = self.vault.vault_adress + "/v1" + path
        request = self.vault.requests_request(
            "LIST", address, headers=self.vault.token_header
        )
        try:
            data = json.loads(request.content)["data"]["keys"]
        except json.decoder.JSONDecodeError:
            logging.exception("Listing the group %s lead to the following error:", path)
            exit(1)
        return data

    def delete(self, group_name):
        """ Delete the given group permanently from vault

        :group_name: name of the group
        :returns: None

        """
        path = self.vault.normalize("/identity/group/name" + group_name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Deleting the group: %s", address)
        self.vault.requests_request("DELETE", address, headers=self.vault.token_header)

    def add(self, group_name, data):
        """ Add the given group with the given data

        :group_name: name of the new/updated group
        :data: data of the group as string
        :returns: None

        """
        path = self.vault.normalize("/identity/group/name/" + group_name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Adding the group: %s", address)
        payload = json.dumps(data)
        response = self.vault.requests_request(
            "POST", address, headers=self.vault.token_header, data=payload
        )

    def read(self, group_name):
        """ read the details of the given group

        :group_name: name of the group
        :returns: group details as string

        """
        path = self.vault.normalize("/identity/group/name/" + group_name)
        address = self.vault.vault_adress + "/v1" + path
        print(address)
        logging.info("Reading the group: %s", address)
        response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        group_details = response.json()["data"]
        return group_details


def add(args, vault):
    """Run this module
    :returns: None

    """
    with open(args.datafile, 'r') as f:
        data = f.read()
        vault.group.add(args.group_name, data)


def delete(args, vault):
    """Run this module
    :returns: None

    """
    vault.group.delete(args.group_name)


def list_groups(args, vault):
    """Run this module
    :returns: None

    """
    group_list = vault.group.list()
    for group in group_list:
        print(group)


def read(args, vault):
    """Run this module
    :returns: None

    """
    print(args.group_name)
    group_details = vault.group.read(args.group_name)
    print(group_details)


def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    add_parser = subparsers.add_parser("group-add")
    del_parser = subparsers.add_parser("group-del")
    list_parser = subparsers.add_parser("group-list")
    read_parser = subparsers.add_parser("group-read")

    add_parser.set_defaults(func=add)
    del_parser.set_defaults(func=delete)
    list_parser.set_defaults(func=list_groups)
    read_parser.set_defaults(func=read)

    for parser in [add_parser, del_parser, read_parser]:
        parser.add_argument(
            "group_name",
            help="name of the group",
        )

    add_parser.add_argument("datafile", help="filename containing group data")
