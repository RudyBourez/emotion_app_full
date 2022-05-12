from datetime import date
from typing import Dict
from fastapi import FastAPI
import uvicorn
import pandas as pd
import sqlite3
import pickle

app = FastAPI()

@app.get('/')
def main():
    return {"Hello World"}

@app.get('/patients_name')
def get_patients_name():
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    df = pd.DataFrame()
    df["first_name"] = [name[0] for name in cursor.execute("SELECT first_name FROM user")]
    df["last_name"] = [name[0] for name in cursor.execute("SELECT last_name FROM user")]
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    return df["full_name"].to_json(orient="index")

@app.get("/get_dates")
def get_dates():
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    df = pd.DataFrame()
    rows = cursor.execute("SELECT publication_date FROM texte").fetchall()
    liste = [row[0] for row in rows]
    df["date"] = pd.date_range(start=min(liste), end=max(liste))
    return df["date"].dt.strftime("%d-%m-%Y").to_json(orient="index")

@app.get("/patients_info/{patient}")
def get_infos(patient):
    liste = patient.split(" ")
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT first_name,last_name,email,birthdate
        FROM user 
        WHERE first_name = ?
        AND last_name = ?;
        """, (liste[0], liste[1])
        ).fetchone()
    return row   

@app.get("/patients_list")
def get_all_patients():
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT *
        FROM user;
        """
        ).fetchall()
    df = pd.DataFrame()
    df["infos"] = [row for row in rows]
    return df["infos"].to_json(orient='index')   

@app.get("/get_entry/{patient}")
def get_last_entry(patient):
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT text
        FROM text as t
        JOIN user as u
        ON t.user_id = u.id
        WHERE t.date_publication = ;
        """
        ).fetchone()
    return row   



@app.post('/modify')
def post_entry(data: Dict):
    return data

@app.post('/delete')
def delete_entry(data: str):
    pass

@app.post('/add')
def modify_entry(data: Dict):
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    duplicate = cursor.execute(
        """SELECT * FROM user WHERE email = ?
        """, data.email).fetchone()
    if not duplicate:
        cursor.execute(
            """INSERT INTO user(first_name, last_name, email, birthdate)
            VALUES (?,?,?,?)
            """, data.keys()
            )
        return {"Successfully added to the database"}
    else:
        return {"This patient already exists in the database"}

if __name__ == "__main__":
    uvicorn.run("main:app")