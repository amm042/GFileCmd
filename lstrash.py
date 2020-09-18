#!/usr/bin/env python3
import logging
import utils
from tabulate import tabulate
from pprint import pprint
import shutil
import pickle
import os
import json

term_columns, term_rows = shutil.get_terminal_size((80,25))

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    ]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='List trashed files on a given day')
    parser.add_argument('output',
                        help='Name of file to write file list to (json).')
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

    filelist = list()
    try:
        nextpage = None
        q=" and ".join([
        "trashed = true",
        "modifiedTime >= '2000-09-01T00:00:00.000Z'",
        "modifiedTime < '2020-09-17T00:00:00.000Z'"])

        while True:
            trashfiles = svc.files().list(
                q=q,
                pageToken = nextpage,
                fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime, trashed)").execute()

            logging.info("got {} files.".format(len(trashfiles['files'])))
            filelist += trashfiles['files']

            # for fileinfo in trashfiles['files']:
            #     print("-"*40)
            #     pathnames = list(map(lambda x: utils.full_path(svc, x),
            #                          fileinfo['parents']))
            #     pathmatch = [x.startswith('My Drive\\Department Public\\ABET\\ABET Cycle F14 - S20\\') for x in pathnames]
            #
            #     if any(pathmatch):
            #         print("UNTRASH --> ", pathnames, '\\', fileinfo['name'])
            #
            #         pprint(svc.files().update(
            #             fileId=fileinfo['id'],
            #             body={'trashed':False},
            #             fields='id, name, trashed'
            #         ).execute(), width=term_columns)
            #     else:
            #         print("SKIP --> ", pathnames, '\\', fileinfo['name'])

            nextpage = trashfiles['nextPageToken']
    except KeyError as x:
        print (x)
        # all done
        pass
    except KeyboardInterrupt:
        logging.info("ctrl-c ABORT.")
    finally:
        logging.info("Writing output with {} files.".format(len(filelist)))
        with open(args.output, 'w') as of:
            json.dump(filelist, of)
    # finally:
    #     with open(hfile, 'wb') as fp:
    #         pickle.dump(hist, fp)
    logging.info("End of main, exit.")
    exit(0)
