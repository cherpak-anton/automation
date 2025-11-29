# file: infra/proxy_lambda/source/runner/storage.py

import os
from google.cloud import storage
from runner.log_manager import log  # use global logger

def download_from_gcs(gcs_url: str, local_path: str):
    log(f"download_from_gcs: {gcs_url} → {local_path}")

    if not gcs_url.startswith("gs://"):
        raise ValueError("Invalid GCS URL")

    no_gs = gcs_url.replace("gs://", "")
    bucket_name, *path_parts = no_gs.split("/")
    blob_path = "/".join(path_parts)

    log(f"bucket={bucket_name}, blob={blob_path}")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    blob.download_to_filename(local_path)

    log("download_from_gcs: OK")
    return local_path


def download_dir_from_gcs(gcs_dir: str, local_dir: str):
    log(f"download_dir_from_gcs: {gcs_dir} → {local_dir}")

    if not gcs_dir.startswith("gs://"):
        raise ValueError("Invalid GCS URL")

    no_gs = gcs_dir.replace("gs://", "")
    bucket_name, *prefix_parts = no_gs.split("/")
    prefix = "/".join(prefix_parts)

    if not prefix.endswith("/"):
        prefix += "/"

    log(f"bucket={bucket_name}, prefix={prefix}")

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for blob in client.list_blobs(bucket, prefix=prefix):
        rel = blob.name[len(prefix):]
        if not rel:
            continue

        local_file = os.path.join(local_dir, rel)
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        blob.download_to_filename(local_file)
        log(f"downloaded: {rel}")

    log("download_dir_from_gcs: OK")
    return local_dir
