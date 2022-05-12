import sqlite3
import csv

con = sqlite3.connect("storage/emotion_db.db")

cursor = con.cursor()

cursor.execute(
    '''CREATE TABLE IF NOT EXISTS user (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    birthdate DATE
    );
    '''
)
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS texte (
    id NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    entered_text TEXT,
    publication_date DATE NOT NULL
    );
    '''
)

text_file = open("BDD/text.csv")
user_file = open("BDD/user.csv")

text_rows = csv.reader(text_file, delimiter='|')
user_rows = csv.reader(user_file, delimiter='|')

cursor.executemany("INSERT INTO user VALUES (?,?,?,?,?)", user_rows)
cursor.executemany("INSERT INTO texte VALUES (?,?,?,?)", text_rows)

con.commit()