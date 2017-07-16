import os
import sys
from azure.storage import blob

from utils import RetryHandler

class BlobStorage(object):
    def __init__(self, account_name, account_key):
        # Create the blob client, for use in obtaining references to
        # blob storage containers and uploading files to containers.
        self.blob_client = blob.BlockBlobService(account_name=account_name, account_key=account_key)

    def list_files(self, container_name, dir_path):
        """Returns a list of blob names that are in the specified directory"""
        blobs = RetryHandler.retry(lambda: self.blob_client.list_blobs(container_name, prefix=dir_path))
        for b in blobs:
            yield b.name

    def download_file(self, container_name, file_path, local_path):
        RetryHandler.retry(lambda: self.blob_client.get_blob_to_path(container_name, file_path, local_path))

    def upload_file(self, container_name, file_path):
        blob_name = os.path.basename(file_path)
        RetryHandler.retry(lambda: self.blob_client.create_blob_from_path(container_name, blob_name, file_path))

