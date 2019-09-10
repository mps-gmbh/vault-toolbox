"""
Class for wrapping the user part of the vault api. This has no claim to be a
full representation of the api but rather to provide convenience functions that
are needed by MPS GmbH.  However, extensions are most welcome.

Author: Janosch Deurer
Mail: deurer@mps-med.de

"""
import json
import logging
import random
import string

class User:

    """Class for wrapping the user part of the vault api."""

    def __init__(self, vault):
        self.vault = vault

    def add(self, firstname, lastname, password=None):
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
        # TODO: make organization configurable
        metadata = {
            "name": firstname + "_" + lastname,
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
                for _ in range(16)
            )
        # Add the user in vault
        address = self.vault.vault_adress + "/v1/auth/userpass/users/" + username
        data = json.dumps({"password": password})
        logging.info("Creating userpass login for: %s", username)
        self.vault.requests_request("POST", address, headers=self.vault.token_header, data=data)
        return password

    def _add_entity(self, data):
        """ Add entity to vault

        :data: Metadata that will be attached to the entity
        :returns: None

        """
        # Add the user in vault
        address = self.vault.vault_adress + "/v1/identity/entity"
        payload = json.dumps(data)
        logging.info("Creating entity with data: %s ", data)
        request = self.vault.requests_request(
            "POST", address, headers=self.vault.token_header, data=payload
        )
        try:
            user_id = json.loads(request.content)["data"]["id"]
        except json.decoder.JSONDecodeError:
            # If there was content, maybe this is actually an error
            if request.content:
                logging.exception("Error while decoding the following json:")
                raise
            else:
                logging.error(
                    "An empty response was returned, seems like the user already exists"
                )
                logging.debug("Loading userid manually")
                user_id = self._get_entity_id(data["name"])

        return user_id

    def _add_alias(self, username, entity_id):
        """ Add an alias between the given userpass username and the given entity.

        :username: userpass username
        :entity_id: id of the entity for the alias

        """
        # Get mount accessor of userpass
        address = self.vault.vault_adress + "/v1/sys/auth"
        request = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        userpass_accessor = json.loads(request.content)["userpass/"]["accessor"]

        # Add the user in vault
        address = self.vault.vault_adress + "/v1/identity/entity-alias"
        payload = json.dumps(
            {
                "name": username,
                "canonical_id": entity_id,
                "mount_accessor": userpass_accessor,
            }
        )
        request = self.vault.requests_request(
            "POST", address, headers=self.vault.token_header, data=payload
        )

    def del_userpass_user(self, user):
        """ Delete the given userpass user
        :returns: None

        """
        address = self.vault.vault_adress + "/v1/auth/userpass/users/" + user
        self.vault.requests_request("DELETE", address, headers=self.vault.token_header)

    def del_entity(self, entity):
        """Delte the given entity

        :enity: Name of the entity
        :returns: None

        """
        address = self.vault.vault_adress + "/v1/identity/entity/name/" + entity
        self.vault.requests_request("DELETE", address, headers=self.vault.token_header)

    def get_userpass_users(self):
        """ Get all users
        :returns: Users

        """
        address = self.vault.vault_adress + "/v1/auth/userpass/users"
        request = self.vault.requests_request("LIST", address, headers=self.vault.token_header)
        return json.loads(request.content)["data"]["keys"]

    def get_entities(self):
        """ Get all entities in vault
        :returns: Iterator over entities

        """
        address = self.vault.vault_adress + "/v1/identity/entity/name"
        request = self.vault.requests_request("LIST", address, headers=self.vault.token_header)
        entity_names = json.loads(request.content)["data"]["keys"]
        for name in entity_names:
            yield self.get_entity_by_name(name)


    def get_entity_by_name(self, name):
        """Resolve entity name to full entity information

        :name: name of the entity
        :returns: Dict with entity information

        """
        address = self.vault.vault_adress + "/v1/identity/entity/name/" + name
        request = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        # If user does not exist return None
        if request.status_code == 404:
            return None
        return json.loads(request.content)["data"]


    def _get_entity_id(self, user):
        """Get id for the given user
        :returns: UserId

        """
        address = self.vault.vault_adress + "/v1/identity/entity/name/" + user
        request = self.vault.requests_request("GET", address, headers=self.vault.token_header)
        return json.loads(request.content)["data"]["id"]




def add(args, vault):
    """Run add subcommand
    :returns: None

    """
    password = vault.add_user(args.firstname, args.lastname)
    token = vault.wrap({"password": password})
    unwrap = vault.unwrap_str(token)
    print(unwrap)

def delete(args, vault):
    """Run delte subcommand
    :returns: None

    """
    user = vault.get_entity_by_name(args.user)
    # TODO: test this
    if user is None:
        logging.error("The given user does not exist, %s%s",
                      "please choose one of the following users:\n\n",
                      "\n".join([entity["name"] for entity in vault.get_entities()]))
        exit(1)
    aliases = user["aliases"]
    for alias in aliases:
        logging.info("Deleting alias %s", alias["name"])
        vault.del_userpass_user(alias["name"])
    logging.info("Deleting entity %s", args.user)
    vault.del_entity(args.user)

def list_user(_, vault):
    """Entrypoint when used as an executable
    :returns: None

    """

    users = vault.get_userpass_users()
    print("## Userpass users:\n")
    for user in users:
        print(user)


    print("\n## Entities:\n")
    users = vault.get_entities()
    for user in users:
        print(user["name"])

    print("\n## Entity aliases:\n")
    users = vault.get_entities()
    for user in users:
        print(user["name"] + " -> aliases:" + str([alias["name"] for alias in user["aliases"]]))




def parse_commandline_arguments(subparsers):
    """ Commandline argument parser for this module
    :returns: None

    """
    add_parser = subparsers.add_parser("user-add")
    del_parser = subparsers.add_parser("user-del")
    parser = subparsers.add_parser("user-list")

    add_parser.set_defaults(func=add)
    del_parser.set_defaults(func=delete)
    parser.set_defaults(func=list_user)

    add_parser.add_argument("firstname", help="Firstname of vault user to create")
    add_parser.add_argument("lastname", help="Lastname of vault user to create")

    del_parser.add_argument("user", help="Vault user to delete")
