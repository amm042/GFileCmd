#!/bin/env python3
import logging
import utils
from pprint import pprint
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    ]


def copy_folder(src, dst, recursive, link):
    logger = logging.getLogger(__name__)

    svc = utils.get_gdrive_service(SCOPES=SCOPES)
    print("Source: ", utils.full_path(svc, src, tpath=[]))
    print("Destn:  ", utils.full_path(svc, dst, tpath=[]))

    for fileinfo in utils.iterfiles(svc, parent=src):
        if dst not in fileinfo['parents']:
            if link:
                update_result = svc.files().update(
                    fileId=fileinfo['id'],
                    addParents=dst,
                    fields='id, parents'
                    ).execute()
                print("update result ", update_result)
            else:
                raise NotImplementedError("TODO")
    utils.list_files(utils.iterfiles(svc, parent=src))
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Copy files/folders on google drive')
    parser.add_argument('source',
                        help='Source folder to copy from.')
    parser.add_argument('dest',
                        help='Destination folder to copy to.')
    parser.add_argument('--recursive','-r', default=False,
                        action="store_true",
                        help='Recursive copy')
    parser.add_argument('--link', '-l', default=False,
                        action="store_true",
                        help='Link files instead of copy')
    levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument('--log-level', default='DEBUG', choices=levels)

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level,
                        format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s')

    logging.debug("Got args: {}".format(args))

    if args.recursive:
        raise NotImplementedError("TODO")

    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
    copy_folder(args.source, args.dest, args.recursive, args.link)

    logging.info("End of main, exit.")
    exit(0)
