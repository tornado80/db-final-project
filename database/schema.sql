CREATE DATABASE db_final_project;

\c db_final_project

CREATE DOMAIN ISBN CHAR(13); /* 13-digit ISBN (10-digit ISBN are blank padded) */

CREATE TABLE publisher (
    id INT PRIMARY KEY,
    name VARCHAR(300)
);

CREATE TABLE book (
    isbn ISBN PRIMARY KEY,
    title VARCHAR(300),
    comment TEXT,
    edition INT,
    published_date DATE,
    publisher_id INT,
    CONSTRAINT fk_publisher_id FOREIGN KEY publisher_id REFERENCES publisher(id)
);

CREATE TABLE lang (
    id INT PRIMARY KEY,
    name VARCHAR(20)
);

/*
It is assumed each edition and translation of a book has different ISBNs. 
Therefore different groups of translators may translate a single book (here an original book) to a single destination language.
And each translation work is recorded separately with its translators.
All of these translated books have a reference to the original book for real authors retrieval.
Also I have inferred from the sentence "A book may have multiple languages" that an original book (written by authors) may be multilingual hence multivalued.

SO HERE we have considered two subclasses of BOOK.

FIRST is ORIGINAL_BOOK which has a reference to BOOK.
It states that this book has been written by some authors and is NOT a translated book.
Hence it is referenced for as many authors as there exist for the book in BOOK_AUTHOR.
Also based on whether it is monolingual or multilingual, for as many languages as used in the book, there would be a record in BOOK_LANGUAGE.

SECOND is TRANSLATED_BOOK which has again a reference to BOOK.
It states that this book has been translated.
Thus it is referenced for as many translators as there exist for the translation work in BOOK_TRANSLATOR.
It also references the original book thereby for retrieval of authors.
Note that a translated book can ONLY be monolingual.

Each instance of a book is recorded in BOOK_INSTANCE.
With this approach, it could be recorded who has borrowed which instance and thereby health of the instance could be determined.
*/

CREATE TABLE original_book (
    isbn ISBN PRIMARY KEY,
    CONSTRAINT fk_isbn FOREIGN KEY isbn REFERENCES book(isbn)
);

CREATE TABLE translated_book (
    isbn ISBN PRIMARY KEY,
    original_isbn ISBN, /* The book from which translators have translated. */
    lang_id INT, /* The destination language to which translators has translated the book. It is obviously single-valued not multivalued. */
    CONSTRAINT fk_lang_id FOREIGN KEY lang_id REFERENCES lang(id),
    CONSTRAINT fk_isbn FOREIGN KEY isbn REFERENCES book(isbn),
    CONSTRAINT fk_original_isbn FOREIGN KEY original_isbn REFERENCES original_book(isbn)
);

CREATE TABLE book_instance (
    id INT,
    isbn ISBN,
    year_added_to_library DATE,
    PRIMARY KEY (id, isbn),
    CONSTRAINT fk_isbn FOREIGN KEY isbn REFERENCES book(isbn),
);

CREATE TABLE book_language (
    isbn ISBN,
    lang_id INT,
    PRIMARY KEY (isbn, lang_id),
    CONSTRAINT fk_lang_id FOREIGN KEY lang_id REFERENCES lang(id),
    CONSTRAINT fk_isbn FOREIGN KEY isbn REFERENCES original_book(isbn),
);

CREATE TABLE author (
    id INT PRIMARY KEY,
    name VARCHAR(300)
);

CREATE TABLE book_author (
    author_id INT,
    book_isbn ISBN,
    PRIMARY KEY (author_id, book_isbn),
    CONSTRAINT fk_author_id FOREIGN KEY author_id REFERENCES author(id),
    CONSTRAINT fk_book_isbn FOREIGN KEY book_isbn REFERENCES original_book(isbn), /* Only original books have authors. */
);

CREATE TABLE translator (
    id INT PRIMARY KEY,
    name VARCHAR(300)
);

CREATE TABLE book_translator (
    translator_id INT,
    book_isbn ISBN,
    PRIMARY KEY (translator_id, book_isbn),
    CONSTRAINT fk_translator_id FOREIGN KEY translator_id REFERENCES translator(id),
    CONSTRAINT fk_book_isbn FOREIGN KEY book_isbn REFERENCES translated_book(isbn),
);

CREATE TABLE genre (
    id INT PRIMARY KEY,
    name VARCHAR(300)
);

CREATE TABLE book_genre (
    genre_id INT,
    book_isbn ISBN,
    PRIMARY KEY (genre_id, book_isbn),
    CONSTRAINT fk_genre_id FOREIGN KEY genre_id REFERENCES genre(id),
    CONSTRAINT fk_book_isbn FOREIGN KEY book_isbn REFERENCES book(isbn),
);

CREATE TABLE member (
    id INT PRIMARY KEY,
    full_name VARCHAR(300),
    birth_date DATE,
    join_date DATE,
    address TEXT,
    contact TEXT /* It is not specified what exactly the contact is. */
);

CREATE TABLE borrow (
    id INT PRIMARY KEY,
    member_id INT,
    instance_id INT,
    instance_isbn ISBN,
    borrowed_date DATE,
    return_date DATE,
    CONSTRAINT fk_member_id FOREIGN KEY member_id REFERENCES member(id),
    CONSTRAINT fk_instance FOREIGN KEY (instance_id, instance_isbn) REFERENCES book_instance(id, isbn),
);