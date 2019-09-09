# Vault-Toolbox

```bash
./vault-toolbox.py --help
usage: vault_toolbox.py [-h] [--logfile LOGFILE] [-v | -q]
                        {unwrap,export,list_users,add_user,del_user,del_secret,import}
                        ...

positional arguments:
  {unwrap,export,list_users,add_user,del_user,del_secret,import}
                        subcommand

optional arguments:
  -h, --help            show this help message and exit
  --logfile LOGFILE     path to a file the output is passed to
  -v, --verbosity       increase output verbosity
  -q, --quiet           no output except errors
```

Documentation for all subcommands can be found with:

```bash
./vault-toolbox.py <subcommand> --help
```

<!-- TODO: add more documentation -->

