import os
from google.cloud import storage

def download_from_gcs(gcs_url: str, local_path: str):
    """
    gcs_url format: gs://bucket/path/file.zip
    """
    if not gcs_url.startswith("gs://"):
        raise ValueError("Invalid GCS URL")

    no_gs = gcs_url.replace("gs://", "")
    bucket_name, *path_parts = no_gs.split("/")
    blob_path = "/".join(path_parts)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    blob.download_to_filename(local_path)

    return local_path

