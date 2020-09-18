#!/usr/bin/env python3
import logging
import utils
from tabulate import tabulate
from pprint import pprint
import shutil
term_columns, term_rows = shutil.get_terminal_size((80,25))

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    ]
def listdrive(svc, recursive=None, **kwargs):
    for fileinfo in utils.iterfiles(svc, **kwargs):

        # if 'parents' in fileinfo:
        #     fileinfo['parent_name'] = list(map(
        #         lambda p: utils.full_path(svc, p),
        #         fileinfo['parents']))
        # if 'parent' in kwargs:
        #     pathname = "{}\\{}".format(utils.full_path(svc, kwargs['parent']), fileinfo['name'])
        # else:
        #     pathname = "\\{}".format(fileinfo['name'])
        # print(pathname, "-"*(max(1,term_columns-len(pathname)-1)))
        pprint(fileinfo, width=term_columns)

    if recursive:
        for pathinfo in utils.iterfiles(svc, parent=kwargs['parent'], is_folder=True):
            #print("-"*term_columns)
            #pprint(pathinfo, width=term_columns)
            listdrive(svc, recursive=True,
                    trashed=kwargs["trashed"],
                    parent=pathinfo["id"],
                    name=kwargs["name"])
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='List detailed info for files/folders on google drive')
    parser.add_argument('--name', '-n', default=None,
                        help='Name of file/folder id to list.')
    parser.add_argument('--trashed','-t', default=None,
                        action="store_true",
                        help='Trashed files')
    parser.add_argument('--parent','-p', default=None,
                        help='Parent folder id')
    parser.add_argument('--recursive','-r', default=False,
                        action="store_true",
                        help='Recursive list')
    levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument('--log-level', default='DEBUG', choices=levels)

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level,
                        format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
    logging.debug("Got args: {}".format(args))
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

    logger = logging.getLogger(__name__)

    svc = utils.get_gdrive_service(SCOPES=SCOPES)

    try:
        listdrive(svc,
                  trashed=args.trashed,
                  parent=args.parent,
                  name=args.name,
                  recursive=args.recursive)
    except KeyboardInterrupt:
        logging.info("ctrl-c ABORT.")
    logging.info("End of main, exit.")
    exit(0)
