from fastapi import FastAPI
import uvicorn
import pandas as pd
import sqlite3
from datetime import datetime

app = FastAPI()

@app.get('/')
def main():
    return {"Hello World"}

@app.get('/patients_name')
def get_patients_name():
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    df = pd.DataFrame()
    df["first_name"] = [name[0] for name in cursor.execute("SELECT first_name FROM user")][1:]
    df["last_name"] = [name[0] for name in cursor.execute("SELECT last_name FROM user")][1:]
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    return df["full_name"].to_json(orient="index")

@app.get("/get_dates")
def get_dates():
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    df = pd.DataFrame()
    min_date = pd.to_datetime([item[0] for item in cursor.execute("SELECT MIN(publication_date) FROM texte")][0], format='%Y-%m-%d')
    max_date = pd.to_datetime([item[0] for item in cursor.execute("SELECT MAX(publication_date) FROM texte")][0], format='%Y-%m-%d')
    # df["date"] = pd.date_range(start=pd.Timestamp(pd.to_datetime(min_date)), end=pd.Timestamp(pd.to_datetime(max_date)))
    return min_date

@app.get("/patients_info/{patient}")
def get_infos(patient):
    liste = patient.split(" ")
    print(liste)
    conn = sqlite3.connect("../storage/emotion_db.db")
    cursor = conn.cursor()
    df = pd.DataFrame
    df["informations"] = [item[0] for item in cursor.execute("SELECT * FROM user WHERE user.first_name == ? AND user.last_name == ?",liste)]
    return df["information"].to_json(orient="index")
    



if __name__ == "__main__":
    uvicorn.run("main:app")