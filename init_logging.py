"""
Common methods for logging

Author: Janosch Deurer
E-Mail: deurer@mps-med.de

"""

import logging


def init_logging(commandline_args):
    """Initialize logging as given in the commandline arguments

    :commandline_args: namespace with commandline arguments including verbosity
    and logfile if given
    :returns: None

    """
    loglevel = "INFO"
    if commandline_args.verbosity:
        loglevel = "DEBUG"
    if commandline_args.quiet:
        loglevel = "ERROR"

    logfile = commandline_args.logfile

    # If logfile is given, generate a new logger with file handling
    if logfile:
        filehandler = logging.FileHandler(logfile, "a")
        formatter = logging.Formatter()
        filehandler.setFormatter(formatter)
        logger = logging.getLogger()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger.addHandler(filehandler)

    loglevel = getattr(logging, loglevel.upper())
    logging.getLogger().setLevel(loglevel)
