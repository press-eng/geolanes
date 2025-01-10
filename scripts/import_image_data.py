import argparse
from datetime import datetime

import firebase_admin
import pymongo
import requests
from firebase_admin import credentials, firestore, storage

COLLECTION_PATH = "tours"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--credentials",
        "-c",
        type=str,
        required=True,
        help="Path to the firebase credentials file",
    )
    args = parser.parse_args()
    credentials_path = args.credentials

    mongo_client = pymongo.MongoClient("")
    attractions = mongo_client.geolanes.attractions

    app_old = firebase_admin.initialize_app(
        credential=credentials.Certificate(credentials_path), name="old_app"
    )
    app_new = firebase_admin.initialize_app(
        credential=credentials.Certificate("./serviceAccountKey.json"), name="new_app"
    )

    storage_bucket_new = storage.bucket(name="geolanes-2.appspot.com", app=app_new)

    db_old = firestore.client(app=app_old)

    col_ref = db_old.collection(COLLECTION_PATH)
    docs = col_ref.stream()

    firebase_docs = [d.to_dict() for d in docs]
    mongo_docs = [d for d in attractions.find({"source": "imported"})]
    new_docs = [
        fd
        for fd in firebase_docs
        if not next((md for md in mongo_docs if fd.get("name") == md["title"]), None)
    ]

    for doc_data in new_docs:
        print(f"Document ID: {doc_data.get('id')}")

        image_url = doc_data.get("imageURL")
        response = None
        blob = None
        if image_url:
            response = requests.get(image_url, stream=True)

        if response and response.status_code == 200:
            image_data = response.content

            blob = storage_bucket_new.blob(
                f"imported/images/{image_url.split('/')[-1]}"
            )
            blob.upload_from_string(image_data)
            blob.make_public()

        geopoint = doc_data.get("location")

        attractions.insert_one(
            {
                "title": doc_data.get("name"),
                "description": doc_data.get("long-desc"),
                "lat": geopoint.latitude if geopoint else None,
                "lng": geopoint.longitude if geopoint else None,
                "source": "imported",
                "updated_at": datetime.now(),
                "address": doc_data.get("address"),
                "images": (
                    [blob.public_url]
                    if blob
                    else [
                        "https://firebasestorage.googleapis.com/v0/b/geolanes-2.appspot.com/o/images%2Fplaceholder.webp?alt=media&token=9ca262a0-5a28-4ebe-aee5-b2b977ff49d8"
                    ]
                ),
            }
        )


if __name__ == "__main__":
    main()
