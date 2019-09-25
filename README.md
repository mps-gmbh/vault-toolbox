# Vault-Toolbox

```bash
./vault_toolbox.py --help
usage: vault_toolbox.py [-h] [--logfile LOGFILE] [-v | -q]
                        {secret-add,secret-del,user-add,user-del,user-list,totp-add,totp-list,totp-read,totp-del,totp-import,unwrap,export,import_from_csv}
                        ...

positional arguments:
  {secret-add,secret-del,user-add,user-del,user-list,totp-add,totp-list,totp-read,totp-del,totp-import,unwrap,export,import_from_csv}
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

## Tab Completion

This project uses argcomplete to provide commandline tab completion. Installation instructions can be found here: [https://argcomplete.readthedocs.io/en/latest/#installation]()

## Config

Some of the commandline arguments can be given in the `config.yaml`. Copy the example file and adapt it to your needs:
```bash
cp ./config_template.yaml config.yaml
```

## TOTP QR-Codes

The `totp-import` command needs a TOTP key url string as an argument. For many providers this is given as a QR-Code. If so save the image of the QR-Code and install `zbar-tools`:
```bash
sudo apt-get install zbar-tools
```
Then you can read the url form the image:
```bash
zbarimg "image-file-name.jpg"
```

<!-- TODO: add more documentation -->
<!-- TODO: add argcomplete docu -->

