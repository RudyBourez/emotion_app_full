from typing import Dict
from fastapi import FastAPI
import uvicorn
import pandas as pd
import sqlite3
from datetime import datetime
import pickle

def open_db():
    return sqlite3.connect("../storage/emotion_db.db", check_same_thread=False)

def close_db(conn):
    conn.commit()
    conn.close()

app = FastAPI()

@app.get('/patients_name')
def get_patients_name():
    conn = open_db()
    cursor = conn.cursor()
    df = pd.DataFrame()
    df["first_name"] = [name[0] for name in cursor.execute("SELECT first_name FROM user")]
    df["last_name"] = [name[0] for name in cursor.execute("SELECT last_name FROM user")]
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    close_db(conn)
    return df["full_name"].to_json(orient="index")

@app.get("/get_dates")
def get_dates():
    conn = open_db()
    cursor = conn.cursor()
    df = pd.DataFrame()
    rows = cursor.execute("SELECT publication_date FROM texte").fetchall()
    liste = [row[0] for row in rows]
    df["date"] = pd.date_range(start=min(liste), end=max(liste))
    close_db(conn)
    return df["date"].dt.strftime("%d-%m-%Y").to_json(orient="index")

@app.get("/patients_info/{patient}")
def get_infos(patient):
    liste = patient.split(" ")
    conn = open_db()
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT first_name,last_name,email,birthdate
        FROM user 
        WHERE first_name = ?
        AND last_name = ?;
        """, (liste[0], liste[1])
        ).fetchone()
    close_db(conn)
    return row   

@app.get("/patients_list")
def get_all_patients():
    conn = open_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT *
        FROM user;
        """
        ).fetchall()
    df = pd.DataFrame()
    df["infos"] = [row for row in rows]
    close_db(conn)
    return df["infos"].to_json(orient='index')   

@app.post('/modify')
def post_entry(data: Dict):
    return data

@app.post('/delete')
def delete_entry(data: Dict):
    conn = open_db()
    cursor = conn.cursor()
    splitted = data["full_name"].split(" ")
    cursor.execute(
        """
        DELETE
        FROM user
        WHERE first_name = ?
        AND last_name = ?
        """,
        (splitted[0], splitted[1])
    )
    close_db(conn)
    return {"Successfully removed from the database"}

@app.post('/add')
def modify_entry(data: Dict):
    conn = open_db()
    cursor = conn.cursor()
    data["birthdate"] = datetime.strptime(data["birthdate"],"%Y-%m-%d").strftime("%d-%m-%Y")
    duplicate = cursor.execute(
        """
        SELECT *
        FROM user
        WHERE email = ?
        """,
        (data["email"],)
        ).fetchone()
    print(data["birthdate"])
    if not duplicate:
        cursor.execute(
            """
            INSERT INTO user(first_name, last_name, birthdate, email)
            VALUES (?,?,?,?)
            """, list(data.values())
            )
        message = {"Successfully added to the database"}
    else:
        message = {"This patient already exists in the database"}
    close_db(conn)
    return message

# ---------------------------------------------Patients-------------------------------------------------

@app.get("/get_entry/{patient}")
def get_last_entry(patient):
    conn = open_db()
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT entered_text, MAX(publication_date)
        FROM texte as t
        JOIN user as u
        ON t.user_id = u.id
        WHERE u.email = ?;
        """,
        (patient,)
        ).fetchone()
    close_db(conn)
    return row[0]   

@app.get('/get_entries/{email}/{date}')
def get_entries(email, date):
    conn = open_db()
    cursor = conn.cursor()
    date = datetime.date(datetime.strptime(date, "%Y-%m-%d"))
    print(email, date, type(date))
    row = cursor.execute(
        """
        SELECT entered_text
        FROM texte as t
        JOIN user as u
        ON u.id = t.user_id
        WHERE publication_date = ?
        AND u.email = ?;
        """,
        (date, email,)
    ).fetchone()
    if row:
        close_db(conn)
        return {row[0]}
    else: 
        close_db(conn)
        return {"There is no entry at this date"}


@app.post("/modify_text")
def modify_text(data: Dict):
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    texte = data["text"]
    email = data["email"]
    cursor.execute(
        """
        UPDATE texte
        SET entered_text = ?
        WHERE publication_date = (
            SELECT MAX(publication_date)
            FROM texte
            JOIN user 
            ON user.id = texte.user_id
            WHERE user.email = ?
        );
        """,
        (texte, email,)
    )
    close_db(conn)
    return {"Last entry successfully updated"}

@app.post('/add_text')
def add_text(data: Dict):
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    email = data["email"]
    user_id = cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
    texte = data["text"]
    today = datetime.date(datetime.now())
    row = cursor.execute(
        """
        SELECT publication_date
        FROM texte
        JOIN user
        ON user.id = texte.user_id
        WHERE publication_date = ?
        AND user.email = ?;
        """,
        (today,email,)
    )
    if row:
        close_db(conn)
        return {"You already have an entry today, please select modify"}
    
    cursor.execute(
        """
        INSERT INTO texte(user_id, entered_text, publication_date)
        VALUES (?, ?, ?)
        """,
        (user_id, texte, today,)
    )
    close_db(conn)
    return {"Entry successfully added to the database"}

if __name__ == "__main__":
    uvicorn.run("main:app")