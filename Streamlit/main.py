import sqlite3
from streamlit import cli as stcli
import sys
import pandas as pd
import streamlit as st
import requests

def init_connection():
    return sqlite3.connect("../storage/emotion_db.db")
    
def get_all_patients_name():
    response = requests.get("http://host.docker.internal:8000/patients_name").json()
    liste = pd.read_json(response,orient="index")
    return liste

def get_dates():
    return requests.get("http://host.docker.internal:8000/get_dates")

def get_informations(patient):
    response = requests.get("http://host.docker.internal:8000/patients_info", patient).json()
    print(response)
    return response

def main():
    def authentification():
        """Returns `True` if the user had the correct mail and password.""" 
        def password_entered():
            """Checks whether a password and a entered by the user is correct."""
            if (
                st.session_state["username"] in st.secrets["passwords"]
                and st.session_state["password"]
                == st.secrets["passwords"][st.session_state["username"]]
            ):
                st.session_state["password_correct"] = True
                # del st.session_state["password"]  # don't store username + password
                # del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False

        if "password_correct" not in st.session_state:
            # First run, show inputs for username + password.
            st.text_input("Username", on_change=password_entered, key="username")
            st.text_input(
                "Password", type="password", on_change=password_entered, key="password"
            )
            return False
        elif not st.session_state["password_correct"]:
            # Password not correct, show input + error.
            st.text_input("Username", on_change=password_entered, key="username")
            st.text_input(
                "Password", type="password", on_change=password_entered, key="password"
            )
            st.error("😕 User not known or password incorrect")
            return False
        else:
            # Password correct.
            if st.session_state["username"] in ["bourez.rudy@gmail.com","manondoublier@yahoo.fr"]:
                st.session_state["admin"] = True
            else:
                st.session_state["admin"] = False
            st.session_state["username"] = st.session_state["username"]
            return True


    if authentification():
        st.markdown(f'<p style="text-align:right">Welcome back, {st.session_state["username"]}<p>', unsafe_allow_html=True)
        if st.session_state["admin"]:
            # -------------------------------------------Sidebar-------------------------------------------------------
            with st.sidebar:
                # --------------------------------Form for patients emotions-----------------------------------
                selection_emotion = st.expander(label="Emotions")
                selection_emotion.header("Emotions of patients")
                    # --------------------------------Choice of the date-------------------------------
                col_emotion1, col_emotion2 = selection_emotion.columns(2)
                custom_date = col_emotion1.button("Date")
                weekly_monthly = col_emotion2.button("Weekly/Monthly")
                    # ---------------------------------------------------------------------------------
                form_emotion = selection_emotion.form(key="Emotions",clear_on_submit=True)
                patient = form_emotion.selectbox(options=patients_name, label="Patient")
                # min_date, max_date = form_emotion.select_slider()
                emotion_submit = form_emotion.form_submit_button("Submit")
                
                # if emotion_submit:
                #     if date == "Monthly":
                #         pass
                #     elif date == "Weekly":
                #         pass
                #     else:
                #         pass
                # ---------------------------------------------------------------------------------------------
                
                # ------------------------------Form for patients informations---------------------------------
                selection_information = st.expander(label="Informations")
                selection_information.header("Patients informations")
                crud = selection_information.selectbox(options=["Add","Delete","Modify"], label="action")
                if crud == "Add":
                    information_form = st.form(key="add", clear_on_submit=True)
                    first_name = information_form.text_input(label="first_name")
                    last_name = information_form.text_input(label="last_name")
                    birthdate = information_form.date_input(label="birthdate")
                    email = information_form.text_input(label="email")
                    information_submit = information_form.form_submit_button("Submit")
                elif crud == "Delete":
                    information_form = st.form(key="delete", clear_on_submit=True)
                    patient_selection = information_form.selectbox(options=patients_name, label="Name")
                else:
                    information_form = st.form(key="delete", clear_on_submit=True)
                    patient_selection = information_form.selectbox(options=patients_name, label="Name")
                    patient_informations = get_informations(patient_selection)
                    first_name = information_form.text_input(label="first_name", value=f"{patient_informations[0]}")
                    last_name = information_form.text_input(label="last_name", value=f"{patient_informations[0]}")
                    birthdate = information_form.date_input(label="birthdate", value=f"{patient_informations[0]}")
                    email = information_form.text_input(label="email", value=f"{patient_informations[0]}")
                    information_submit = information_form.form_submit_button("Submit")
                # ---------------------------------------------------------------------------------------------
        else:
            st.write("Welcome customer")
            
if __name__ == '__main__':
    if st._is_running_with_streamlit:
        conn = init_connection()
        patients_name = get_all_patients_name()
        dates = get_dates()
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())