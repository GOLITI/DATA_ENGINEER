import datetime
import json

# La bibliothèque est une liste de dictionnaires
library = []

# Ajouter un livre
def add_book(title, author, year, category="Inconnu"):
    book = {
        "title": title,
        "author": author,
        "year": year,
        "category": category,
        "date_added": datetime.datetime.now()
    }
    library.append(book)
    print(f"Livre ajouté : {title}")

# Modifier un livre
def modify_book(title, new_title=None, new_author=None, new_year=None, new_category=None):
    for book in library:
        if book["title"] == title:
            if new_title: book["title"] = new_title
            if new_author: book["author"] = new_author
            if new_year: book["year"] = new_year
            if new_category: book["category"] = new_category
            print(f"Livre modifié : {book}")
            return
    print("Livre non trouvé")

# Supprimer un livre
def delete_book(title):
    for book in library:
        if book["title"] == title:
            library.remove(book)
            print(f"Livre supprimé : {title}")
            return
    print("Livre non trouvé")

# Afficher tous les livres
def show_library():
    if not library:
        print("La bibliothèque est vide.")
    else:
        print("Ma bibliothèque :")
        for book in library:
            print(f"- {book['title']}, {book['author']}, {book['year']}, {book['category']}")

# Rechercher un livre par titre ou auteur
def search_book(keyword):
    results = []
    for book in library:
        if keyword.lower() in book['title'].lower() or keyword.lower() in book['author'].lower():
            results.append(book)
    if results:
        print("Résultats de la recherche :")
        for book in results:
            print(f"- {book['title']}, {book['author']}, {book['year']}, {book['category']}")
    else:
        print("Aucun livre trouvé")

# Trier les livres par date d'ajout ou par catégorie
def sort_books(by="date"):
    if by == "date":
        sorted_books = sorted(library, key=lambda x: x['date_added'])
    elif by == "category":
        sorted_books = sorted(library, key=lambda x: x['category'])
    else:
        print("Critère inconnu. Utilisez 'date' ou 'category'.")
        return

    print("Livres triés :")
    for book in sorted_books:
        print(f"- {book['title']}, {book['author']}, {book['year']}, {book['category']}")

# Classe Livre
class Book:
    def __init__(self, title, author, year, category="Inconnu"):
        self.title = title
        self.author = author
        self.year = year
        self.category = category
        self.date_added = datetime.datetime.now()

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "category": self.category,
            "date_added": self.date_added.isoformat()
        }

# Classe Bibliothèque
class Library:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        self.books.append(book)
        print(f"Livre ajouté : {book.title}")

    def modify_book(self, title, new_title=None, new_author=None, new_year=None, new_category=None):
        for book in self.books:
            if book.title == title:
                if new_title: book.title = new_title
                if new_author: book.author = new_author
                if new_year: book.year = new_year
                if new_category: book.category = new_category
                print(f"Livre modifié : {book.to_dict()}")
                return
        print("Livre non trouvé")

    def delete_book(self, title):
        for book in self.books:
            if book.title == title:
                self.books.remove(book)
                print(f"Livre supprimé : {title}")
                return
        print("Livre non trouvé")

    def show_books(self):
        if not self.books:
            print("La bibliothèque est vide.")
        else:
            for book in self.books:
                print(f"- {book.title}, {book.author}, {book.year}, {book.category}")

    def search_book(self, keyword):
        results = [book for book in self.books if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower()]
        if results:
            print("Résultats de la recherche :")
            for book in results:
                print(f"- {book.title}, {book.author}, {book.year}, {book.category}")
        else:
            print("Aucun livre trouvé")

    def sort_books(self, by="date"):
        if by == "date":
            sorted_books = sorted(self.books, key=lambda x: x.date_added)
        elif by == "category":
            sorted_books = sorted(self.books, key=lambda x: x.category)
        else:
            print("Critère inconnu. Utilisez 'date' ou 'category'.")
            return
        print("Livres triés :")
        for book in sorted_books:
            print(f"- {book.title}, {book.author}, {book.year}, {book.category}")

    def save(self, file="library.json"):
        with open(file, "w", encoding="utf-8") as f:
            json.dump([book.to_dict() for book in self.books], f, ensure_ascii=False, indent=4)
            print("Données sauvegardées dans library.json")

    def load(self, file="library.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book(d['title'], d['author'], d['year'], d['category']) for d in data]
                print("Données chargées depuis library.json")
        except FileNotFoundError:
            print("Aucun fichier trouvé, bibliothèque vide.")

# Exemple d'utilisation
ma_bibliotheque = Library()
ma_bibliotheque.load()

ma_bibliotheque.add_book(Book("Les Soleils des Indépendances", "Ahmadou Kourouma", 1970, "Roman"))
ma_bibliotheque.add_book(Book("Allah n’est pas obligé", "Ahmadou Kourouma", 2000, "Roman"))
ma_bibliotheque.add_book(Book("Le Bal des Masques", "Véronique Tadjo", 1990, "Poésie"))
ma_bibliotheque.add_book(Book("La Mémoire amputée", "Werewere Liking", 2004, "Roman"))
ma_bibliotheque.add_book(Book("La Route des esclaves", "Véronique Tadjo", 1999, "Roman historique"))

ma_bibliotheque.show_books()
ma_bibliotheque.search_book("Kourouma")
ma_bibliotheque.sort_books("category")
ma_bibliotheque.save()
