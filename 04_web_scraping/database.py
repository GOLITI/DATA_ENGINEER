import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "library")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "books")


def get_collection():
    """Retourne la collection MongoDB 'library.books'."""
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
    client = MongoClient(uri)
    return client[MONGO_DB][MONGO_COLLECTION]


def insert_books(books: list[dict]) -> dict:
    """
    Insère une liste de livres dans MongoDB.
    Retourne un dict avec le nombre inséré et le nombre de doublons ignorés.
    """
    if not books:
        return {"inserted": 0, "duplicates": 0}

    collection = get_collection()

    # Créer un index UNIQUE sur book_id (empêche les doublons)
    collection.create_index([("book_id", ASCENDING)], unique=True)
    print("   Index UNIQUE créé sur book_id.")

    # Index utile pour les requêtes analytiques
    collection.create_index([("rating", ASCENDING)])
    collection.create_index([("price", ASCENDING)])
    collection.create_index([("source", ASCENDING)])

    try:
        result = collection.insert_many(books, ordered=False)
        return {"inserted": len(result.inserted_ids), "duplicates": 0}
    except BulkWriteError as e:
        inserted = e.details.get("nInserted", 0)
        duplicates = len(e.details.get("writeErrors", []))
        return {"inserted": inserted, "duplicates": duplicates}


def count_books() -> int:
    """Compte le nombre de livres dans la collection."""
    return get_collection().count_documents({})