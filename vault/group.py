"""
Class for wrapping the group part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.
"""
import json
import logging
import yaml


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
        path = self.vault.normalize("/identity/group/name/" + group_name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Deleting the group: %s", address)
        self.vault.requests_request("DELETE", address, headers=self.vault.token_header)

    def add(self, group_name, data={}):
        """ Add the given group with the given data

        :group_name: name of the new/updated group
        :data: data of the group as dict
        :returns: None

        """
        path = self.vault.normalize("/identity/group/name/" + group_name)
        address = self.vault.vault_adress + "/v1" + path
        logging.info("Adding or updating the group: %s", address)
        payload = json.dumps(data)
        self.vault.requests_request(
            "POST", address, headers=self.vault.token_header, data=payload
        )

    def read(self, group_name):
        """ read the details of the given group

        :group_name: name of the group
        :returns: group details as dict

        """
        path = self.vault.normalize("/identity/group/name/" + group_name)
        address = self.vault.vault_adress + "/v1" + path
        response = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        group_details = response.json()["data"]
        return group_details

    def recursive_read(self):
        """ read the details of all groups

        :returns: group details as dict

        """
        groups = self.list()
        for group in groups:
            yield group, self.read(group)

    def yaml_export(self):
        """ export all groups as yaml

        :returns: yaml string

        """
        groups = self.recursive_read()
        group_dict = {}
        for group, group_details in groups:
            group_dict[group] = group_details["policies"]
        return yaml.dump(group_dict, allow_unicode=True)

    def yaml_import(self, groups):
        """ import all groups as yaml

        :groups: group definition as yaml
        :returns: None

        """
        try:
            yaml_groups = yaml.safe_load(groups)
        except yaml.YAMLError:
            logging.exception("Error in yaml:")
            exit(1)
        for group, group_details in yaml_groups.items():
            self.add(group, {"policies": group_details})
        delete_groups = []
        for group in self.list():
            if group not in yaml_groups:
                delete_groups.append(group)

        if delete_groups:
            print("The following groups will be DELETED:")
            for group in delete_groups:
                print(group)
            user_input = input("If you want to continue type yes: ")
            if user_input != "yes":
                print("Aborting deletion")
                return
            for group in delete_groups:
                self.delete(group)




def add(args, vault):
    """Run this module
    :returns: None

    """
    vault.group.add(args.group_name)


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
    print("Policies of " + args.group_name + ":")
    for policy in vault.group.read(args.group_name)['policies']:
        print(policy)


def yaml_export(args, vault):
    """Run this module
    :returns: None

    """
    print(vault.group.yaml_export())


def yaml_import(args, vault):
    """Run this module
    :returns: None

    """
    with open(args.datafile, 'r') as f:
        data = f.read()
    vault.group.yaml_import(data)


def parse_commandline_arguments(subparsers, config):
    """ Commandline argument parser for this module
    :returns: None

    """
    add_parser = subparsers.add_parser("group-add")
    del_parser = subparsers.add_parser("group-del")
    list_parser = subparsers.add_parser("group-list")
    read_parser = subparsers.add_parser("group-read")
    yaml_export_parser = subparsers.add_parser("group-yaml-export")
    yaml_import_parser = subparsers.add_parser("group-yaml-import")

    add_parser.set_defaults(func=add)
    del_parser.set_defaults(func=delete)
    list_parser.set_defaults(func=list_groups)
    read_parser.set_defaults(func=read)
    yaml_export_parser.set_defaults(func=yaml_export)
    yaml_import_parser.set_defaults(func=yaml_import)

    for parser in [add_parser, del_parser, read_parser]:
        parser.add_argument(
            "group_name",
            help="name of the group",
        )
    yaml_import_parser.add_argument("datafile", help="filename containing group data")
