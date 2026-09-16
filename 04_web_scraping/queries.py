from database import get_collection


def top_expensive_books(limit: int = 10):
    """Les N livres les plus chers."""
    col = get_collection()
    return list(col.find(
        {},
        {"_id": 0, "title": 1, "price": 1, "rating": 1}
    ).sort("price", -1).limit(limit))


def top_rated_books(limit: int = 10):
    """Les N livres les mieux notés (avec leur prix)."""
    col = get_collection()
    return list(col.find(
        {},
        {"_id": 0, "title": 1, "rating": 1, "price": 1}
    ).sort([("rating", -1), ("price", -1)]).limit(limit))


def rating_distribution():
    """Distribution des notes (combien de livres par note)."""
    col = get_collection()
    return list(col.aggregate([
        {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]))


def price_stats():
    """Statistiques sur les prix (min, max, moyenne)."""
    col = get_collection()
    result = list(col.aggregate([
        {"$group": {
            "_id": None,
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"},
            "avg_price": {"$avg": "$price"},
            "total": {"$sum": 1},
        }},
    ]))
    return result[0] if result else {}


def price_by_rating():
    """Prix moyen pour chaque note."""
    col = get_collection()
    return list(col.aggregate([
        {"$group": {
            "_id": "$rating",
            "avg_price": {"$avg": "$price"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]))


def stock_summary():
    """Combien de livres en stock vs hors stock."""
    col = get_collection()
    return list(col.aggregate([
        {"$group": {"_id": "$stock", "count": {"$sum": 1}}},
    ]))


def books_per_price_range():
    """Répartition des livres par tranche de prix."""
    col = get_collection()
    return list(col.aggregate([
        {"$bucket": {
            "groupBy": "$price",
            "boundaries": [0, 10, 20, 30, 40, 50, 60, 100],
            "default": "Autre",
            "output": {"count": {"$sum": 1}},
        }},
    ]))


if __name__ == "__main__":
    print("=== Top 5 LIVRES LES PLUS CHERS ===")
    for b in top_expensive_books(5):
        print(f"  {b['title'][:45]:<45} | £{b['price']:>6.2f} | {b['rating']}★")

    print("\n=== TOP 5 LIVRES LES MIEUX NOTÉS ===")
    for b in top_rated_books(5):
        print(f"  {b['title'][:45]:<45} | {b['rating']}★ | £{b['price']:>6.2f}")

    print("\n=== DISTRIBUTION DES NOTES ===")
    for r in rating_distribution():
        print(f"  {r['_id']}★ : {r['count']} livres")

    print("\n=== STATISTIQUES DE PRIX ===")
    stats = price_stats()
    print(f"  Min : £{stats['min_price']:.2f}")
    print(f"  Max : £{stats['max_price']:.2f}")
    print(f"  Moyenne: £{stats['avg_price']:.2f}")
    print(f"  Total : {stats['total']} livres")

    print("\n=== PRIX MOYEN PAR NOTE ===")
    for r in price_by_rating():
        print(f"  {r['_id']}★ : £{r['avg_price']:.2f} (sur {r['count']} livres)")

    print("\n=== RÉPARTITION PAR TRANCHE DE PRIX ===")
    for r in books_per_price_range():
        print(f"  £{r['_id']} : {r['count']} livres")

    print("\n=== STOCK ===")
    for r in stock_summary():
        print(f"  {r['_id']} : {r['count']} livres")