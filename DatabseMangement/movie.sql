CREATE DATABASE IF NOT EXISTS MOVIES;
USE MOVIES;

CREATE USER IF NOT EXISTS 'MOVIE_USER'@'localhost' IDENTIFIED BY 'MOVIE_USER';
GRANT ALL PRIVILEGES ON MOVIES.* TO 'MOVIE_USER'@'localhost';
FLUSH PRIVILEGES;

DROP TABLE IF EXISTS USERS;
CREATE TABLE IF NOT EXISTS USERS(
    id integer unique not null ,
    name VARCHAR(255),
    PRIMARY KEY (id)

);

DROP TABLE IF EXISTS GENRES;
CREATE TABLE IF NOT EXISTS GENRES (
    id int NOT NULL AUTO_INCREMENT,
    genre varchar(255) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO GENRES (genre)
VALUES 			('drama'),
				('comedy'),
                ('thriller'),
                ('action'),
                ('horror'),
                ('adventure'),
                ('family'),
                ('romance'),
                ('history'),
                ('biography'),
                ('fantasy'),
                ('musical'),
                ('sci-fi'),
                ('film-noir'),
                ('war'),
                ('western'),
                ('crime');

DROP TABLE IF EXISTS USER_GENRE;
CREATE TABLE IF NOT EXISTS USER_GENRE(
    user_id int NOT NULL,
    genre_id int NOT NULL,
    PRIMARY KEY (user_id, genre_id),
    FOREIGN KEY (user_id) REFERENCES USERS(id),
    FOREIGN KEY (genre_id) REFERENCES GENRES(id)
);