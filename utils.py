# modified from https://www.thepythoncode.com/article/using-google-drive--api-in-python#List_Files_and_Directories
# and https://gist.github.com/xflr6/d106aa5b561fbac4ce1a9969eba728bb
# by Alan Marchiori 2020
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate
import os.path
import pickle
from pprint import pprint
FOLDER = 'application/vnd.google-apps.folder'

def get_gdrive_service(
    cred_file='credentials.json',
    token_file='token.pickle',
    SCOPES=['https://www.googleapis.com/auth/drive.metadata.readonly']):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)
def list_item_to_row(item):
    """returns a tabulate-compatible row from a file object"""
    # get the File ID
    id = item["id"]
    # get the name of file
    name = item["name"]
    try:
        # parent directory ID
        parents = "{} ({})".format(
            item["parents"],
            full_path(item["parents"]))
    except:
        # has no parrents
        parents = "N/A"
    try:
        # get the size in nice bytes format (KB, MB, etc.)
        size = get_size_format(int(item["size"]))
    except:
        # not a file, may be a folder
        size = "N/A"
    # get the Google Drive type of file
    mime_type = item["mimeType"]
    # get last modified date time
    modified_time = item["modifiedTime"]

    return ((id, name, parents, size, mime_type, modified_time))
def list_files(items):
    """given items returned by Google Drive API, prints them in a tabular way"""
    if not items:
        # empty drive
        print('No files found.')
    else:
        rows = []
        for item in items:
            rows.append(list_item_to_row(item))
        print("Files:")
        # convert to a human readable table
        table = tabulate(rows, headers=["ID", "Name", "Parents", "Size", "Type", "Modified Time"])
        # print the table
        print(table)
def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

__path_cache = {}
def full_path(svc, p):
    """
    trace src to root
    """

    if p in __path_cache:
        return __path_cache[p]

    files = svc.files()
    result = files.get(fileId=p, fields="name, parents").execute()

    allPaths = []
    if 'parents' in result:
        for parentId in result['parents']:
            parentPaths = full_path(svc, parentId)
            __path_cache[parentId] = parentPaths.copy()

            for i,parentPath in enumerate(parentPaths):
                parentPaths[i] = "{}\\{}".format(parentPath, result['name'])

            allPaths += parentPaths
    else:
        # base case, at root, return name
        allPaths = [result['name']]

    __path_cache[p] = allPaths
    return allPaths

def iterfiles(service, name=None,
    is_folder=None, parent=None, trashed=None,
    order_by='folder,name,createdTime',
    fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime, trashed)"):
    q = []
    if trashed is not None:
        q.append("trashed = {}".format(trashed))
    if name is not None:
        q.append("name = '%s'" % name.replace("'", "\\'"))
    if is_folder is not None:
        q.append("mimeType %s '%s'" % ('=' if is_folder else '!=', FOLDER))
    if parent is not None:
        q.append("'%s' in parents" % parent.replace("'", "\\'"))
    params = {'pageToken': None,
        'orderBy': order_by,
        'fields': fields
    }
    if q:
        params['q'] = ' and '.join(q)
    while True:
        response = service.files().list(**params).execute()
        for f in response['files']:
            yield f
        try:
            params['pageToken'] = response['nextPageToken']
        except KeyError:
            return

def walk(service, top='root', by_name=False):
    if by_name:
        top, = iterfiles(service=service, name=top, is_folder=True)
    else:
        top = service.files().get(fileId=top).execute()
        if top['mimeType'] != FOLDER:
            raise ValueError('not a folder: %r' % top)
    stack = [((top['name'],), top)]
    while stack:
        path, top = stack.pop()
        dirs, files = is_file = [], []
        for f in iterfiles(service=service, parent=top['id']):
            is_file[f['mimeType'] != FOLDER].append(f)
        yield path, top, dirs, files
        if dirs:
            stack.extend((path + (d['name'],), d) for d in reversed(dirs))
