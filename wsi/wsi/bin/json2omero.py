import argparse
from getpass import getpass
import logging
import sys

import omero
import omero.clients
from omero.gateway import BlitzGateway

from wsi.data.import_to_omero import OmeroImportHelper


LOGGING_FORMAT = "%(asctime)s %(levelname)-7s [%(name)16s] %(message)s"
LOGGER = logging.getLogger('json2omero')


def set_logging(debug):
    '''
    Set logging level.
    '''
    if debug:
        logging.basicConfig(
            level=logging.DEBUG, format=LOGGING_FORMAT, stream=sys.stdout)
    else:
        logging.basicConfig(
            level=logging.INFO, format=LOGGING_FORMAT, stream=sys.stdout)


def connect_to_server(params):
    LOGGER.debug("Connecting to server")
    conn = omero.client(
        host=params["server"], port=params["port"]
    )
    session = None
    if params["user"] is not None:
        password = params["password"]
        if password is None:
            password = getpass()
        session = conn.createSession(
            username=params["user"],
            password=password
        )
        conn.enableKeepAlive(60)
        session.detachOnDestroy()
    else:
        message = "Not enough details to create a server connection."
        raise Exception(message)
    return conn


def run(params):
    LOGGER.debug("Preparing import")
    omero_client = None
    helper = OmeroImportHelper()
    try:
        omero_client = connect_to_server(params)
        gateway = BlitzGateway(client_obj=omero_client)
        json_list = helper.get_json_list(params["input_dir"])
        LOGGER.debug("Converting %s to OMERO annotations" % json_list)
        image_name_dictionary = helper.get_image_name_dictionary(
            gateway, params["dataset"])
        LOGGER.debug("Images link to the dataset: %s" % image_name_dictionary)
        for json_file in json_list:
            helper.convert_json_to_omero_annotation(
                gateway, json_file, image_name_dictionary
            )
    finally:
        if omero_client is not None:
            omero_client.killSession()


def parse_arguments():
    LOGGER.debug("Parsing arguments")
    description = "Convert JSON to OMERO Annotation"
    width = 225
    column_width = 45
    parser = argparse.ArgumentParser(
        prog='python json2omero.py', description=description,
        formatter_class=lambda
        prog: argparse.HelpFormatter(
            prog, max_help_position=column_width, width=width
        )
    )
    parser.set_defaults(func=run)
    parser.add_argument(
        '-s', '--server',
        help='OMERO server.'
    )
    parser.add_argument(
        '-p', '--port', type=int,
        help='OMERO port.'
    )
    parser.add_argument(
        '-u', '--user',
        help='OEMRO user.'
    )
    parser.add_argument(
        '-w', '--password',
        help='OMERO password.'
    )
    parser.add_argument(
        '--debug', '-d', required=False, action='store_true',
        help='Set the logging level to debug.'
    )
    parser.add_argument('--dry_run', action='store_true')
    parser.add_argument('--input_dir',  required=True,
                        help='Directory with json files.')
    parser.add_argument('--dataset', type=int,  required=True,
                        help="OMERO dataset id with images to annotate")
    args = parser.parse_args()
    set_logging(vars(args)["debug"])
    LOGGER.debug("Logging set to debug.")
    args.func(vars(args))
    return vars(args)


def main():
    parse_arguments()


if __name__ == "__main__":
    main()