-- DATABASE STRUCTURE --

-- Créer la base de données
CREATE DATABASE library_db;

-- Table auteurs
CREATE TABLE authors (
	author_id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	nationality VARCHAR(50),
	birth_date DATE
);

-- Table livres
CREATE TABLE books(
	book_id SERIAL PRIMARY KEY,
	title VARCHAR(150) NOT NULL,
	category VARCHAR(50),
	publication_date INT,
	author_id INT REFERENCES authors(author_id) ON DELETE CASCADE
);

-- Table emprunteurs
CREATE TABLE borrowers(
	borrower_id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	registration_date DATE DEFAULT CURRENT_DATE 
);

-- Table emprunts
CREATE TABLE borrowings(
	borrowing_id SERIAL PRIMARY KEY,
	book_id INT REFERENCES books(book_id) ON DELETE CASCADE,
	borrower_id INT REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
	borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
	due_date DATE NOT NULL,
	return_date DATE
);

-- DATA INSERTION --

-- Insertion des auteurs
INSERT INTO authors(name, nationality, birth_date)
VALUES
('Léopold Sédar Senghor', 'Sénégalais', '1906-10-09'),
('Bernard Binlin Dadié', 'Ivoirien', '1916-01-10'),
('Ahmadou Kourouma', 'Ivoirien', '1927-11-24'),
('Amadou Hampaté Bâ', 'Malien', '1901-05-15');

-- Insertion des livres
INSERT INTO books(title, category, publication_date, author_id)
VALUES
('Chants d''ombre', 'Poésie', 1945, 1),
('Hosties noires', 'Poésie', 1948, 1),
('Climbié l''école', 'Biographies', 1953, 2),
('Le Pagne noir', 'Conte', 1955, 2),
('Afrique debout', 'Poésie', 1950, 2),
('Les Soleils des indépendances', 'Romanesque', 1968, 3),
('Allah n''est pas obligé', 'Romanesque', 2000, 3),
('Ce que vaut la poussière', 'Conte', 1987, 4),
('Amkoullel, l''enfant peul', 'Biographies', 1991, 4);

-- Insertion des emprunteurs
INSERT INTO borrowers(name, email, registration_date)
VALUES
('Marc Goliti', 'goliti@gmail.com', '2026-01-10'),
('Jean Kouassi', 'kouassi@gmail.com', '2026-02-10'),
('Moussa Koné', 'kone@gmail.com', '2026-03-01'),
('Emma Konan', 'konan@gmail.com', '2026-03-02');

-- Insertion des emprunts
INSERT INTO borrowings(book_id, borrower_id, borrow_date, due_date, return_date)
VALUES
(2, 2, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '9 days', NULL),
(6, 4, CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE + INTERVAL '13 days', NULL),
(7, 1, CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE + INTERVAL '10 days', NULL),
(1, 3, '2026-05-02', '2026-05-16', '2026-05-14'),
(8, 2, '2026-06-15', '2026-06-29', '2026-06-29'),
(9, 4, '2026-07-01', '2026-07-15', '2026-07-10'),
(3, 2, '2026-04-10', '2026-04-24', '2026-05-02'),
(4, 3, '2026-03-01', '2026-03-15', '2026-03-25'),
(2, 4, CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE - INTERVAL '6 days', NULL),
(6, 3, CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '16 days', NULL),
(8, 1, CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '31 days', NULL),
(9, 2, CURRENT_DATE - INTERVAL '12 days', CURRENT_DATE - INTERVAL '2 days', NULL);

-- THE QUERIES --

-- Quels sont les livres empruntés cette semaine ?
SELECT books.title titre , borrowings.borrow_date date_emprunt, borrowers.name emprunteur
FROM borrowings
INNER JOIN books ON borrowings.book_id = books.book_id
INNER JOIN borrowers ON borrowings.borrower_id = borrowers.borrower_id
WHERE borrowings.borrow_date >= CURRENT_DATE - INTERVAL '7 days';

-- Quel auteur a publié le plus de livres ?
SELECT a.name nom, COUNT(b.book_id) total_livre
FROM authors a
LEFT JOIN books b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
ORDER BY total_livre DESC
LIMIT 1;

-- Quels emprunteurs ont emprunté le plus de livres sur une période donnée ?
SELECT borrowers.name nom, COUNT(borrowings.borrowing_id) total_emprunt
FROM borrowers
INNER JOIN borrowings ON borrowers.borrower_id = borrowings.borrower_id
WHERE borrowings.borrow_date BETWEEN '2026-05-01' AND '2026-12-31'
GROUP BY borrowers.borrower_id, borrowers.name
ORDER BY total_emprunt DESC;

-- OPTIMIZATION & VIEWS --

-- VIEW
CREATE OR REPLACE VIEW view_active_borrowings AS
SELECT br.borrowing_id, borrowers.name nom_emprunteur, b.title titre_livre, br.borrow_date date_emprunt, br.due_date date_echeance
FROM borrowings br
INNER JOIN borrowers ON br.borrower_id = borrowers.borrower_id
INNER JOIN books b ON br.book_id = b.book_id
WHERE br.return_date IS NULL;

-- INDEXES
CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_borrowings_date ON borrowings(borrow_date);
