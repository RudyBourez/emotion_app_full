from operator import mod
import sqlite3
from streamlit import cli as stcli
import sys
import pandas as pd
import streamlit as st
import requests

    
def get_all_patients_name():
    response = requests.get("http://host.docker.internal:8000/patients_name").json()
    liste = pd.read_json(response,orient="index")
    return liste

def get_dates():
    response = requests.get("http://host.docker.internal:8000/get_dates").json()
    liste = pd.read_json(response,orient="index")
    min_date = liste.min().item()
    max_date = liste.max().item()
    return liste, min_date, max_date

def get_informations(patient):
    response = requests.get(f"http://host.docker.internal:8000/patients_info/{patient}").json()
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
        container = st.container()
        if st.session_state["admin"]:
            # -------------------------------------------Sidebar-------------------------------------------------------
            with st.sidebar:
                # --------------------------------Form for patients emotions-----------------------------------
                selection_emotion = st.expander(label="Emotions")
                selection_emotion.header("Emotions of patients")
                    # --------------------------------Choice of the date-------------------------------
                date_type = selection_emotion.selectbox(options=["", "Unique", "Range"], label="Choose between an unique date or a range of dates")
                    # ---------------------------------------------------------------------------------
                form_emotion = selection_emotion.form(key="Emotions",clear_on_submit=True)
                if date_type != "":
                    patient = form_emotion.selectbox(options=patients_name, label="Patient")
                    if date_type == "Range":
                        min_date, max_date = form_emotion.select_slider("Choose between two dates",options=dates, value=(date_max, date_min))
                        emotion_submit = form_emotion.form_submit_button("Submit")
                        if emotion_submit:
                            response = requests.get(f'http://host.docker.internal:8000/range_prediction/{patient}/{min_date}/{max_date}').json()
                            df = pd.read_json(response, orient="index")
                            container.write(df)
                    elif date_type == "Unique":
                        date_choosed = form_emotion.date_input(label="Choose a date")
                        emotion_submit = form_emotion.form_submit_button("Submit")
                        if emotion_submit:
                            response = requests.get(f'http://host.docker.internal:8000/prediction/{patient}/{date_choosed}').json()[0]
                            container.write(response)
                            
                # ---------------------------------------------------------------------------------------------
                        
                # ------------------------------Form for patients informations---------------------------------
                selection_information = st.expander(label="Informations")
                selection_information.header("Patients informations")
                crud = selection_information.selectbox(options=["","Add","Delete","Modify"], label="Action")
                    # -----------------------------------Patients text---------------------------------------
                patients_text = st.expander(label="Actions")
                patients_text.subheader("vvv Click on the button vvv")
                patients_list = patients_text.button("Get patients list")
                patients_emotions = patients_text.button("Get all emotions")
                    # ---------------------------------------------------------------------------------------

            if crud == "Add":
                information_form = st.form(key="add", clear_on_submit=True)
                first_name_add = information_form.text_input(label="First Name")
                last_name_add = information_form.text_input(label="Last Name")
                birthdate_add = information_form.date_input(label="Birthdate")
                email_add = information_form.text_input(label="Email")
                submit = information_form.form_submit_button("Submit")
            elif crud == "Delete":
                information_form = st.form(key="delete", clear_on_submit=True)
                patient_selection_delete = information_form.selectbox(options=patients_name, label="Name")
                radio = information_form.checkbox("Are you that you want to delete this entry ?")
                submit = information_form.form_submit_button("Delete")
            elif crud == "Modify":
                patient_selection = st.selectbox(options=patients_name, label="Name")
                information_form = st.form(key="modify", clear_on_submit=True)
                patient_informations = get_informations(patient_selection)
                patient_email = patient_informations[2]
                first_name_modify = information_form.text_input(label="First Name", value=patient_informations[0])
                last_name_modify = information_form.text_input(label="Last Name", value=patient_informations[1])
                email_modify = information_form.text_input(label="Email", value=patient_informations[2])
                birthdate_modify = information_form.text_input(label="Birthdate (DD-MM-YYYY)", value = patient_informations[3])
                submit = information_form.form_submit_button("Submit")
                # ---------------------------------------------------------------------------------------------

            # -----------------------------------------Forms---------------------------------------------------------
            if crud !="":
                if submit:
                    if crud == "Delete":
                        if radio:
                            response = requests.post("http://host.docker.internal:8000/delete", json={
                                "full_name": patient_selection_delete})
                            st.success(response.json()[0])
                        else:
                            st.warning("Please, check the box to enable the suppression")

                    elif crud == "Add":
                        response = requests.post("http://host.docker.internal:8000/add",json={
                            "first_name": first_name_add,
                            "last_name": last_name_add,
                            "birthdate": str(birthdate_add),
                            "email": email_add}).json()[0]
                        st.success(response)

                    elif crud == "Modify":
                        response = requests.post("http://host.docker.internal:8000/modify",json={
                            "first_name": first_name_modify,
                            "last_name": last_name_modify,
                            "email": email_modify,
                            "birthdate": birthdate_modify,
                            "user" : patient_email
                            }).json()[0]
                        st.success(response)

            if patients_list:
                response = requests.get("http://host.docker.internal:8000/patients_list").json()
                df = pd.read_json(response ,orient="index")
                df.columns = ["id", "First Name", "Last Name", "E-mail", "Birthdate"]
                df.drop("id",axis=1, inplace=True)
                st.subheader("All patients informations")
                st.write(df)
            # ------------------------------------------------------------------------------------------------------


        else:
            with st.sidebar:
                action = st.radio(label="Options", options=["Add an entry", "Modify last entry", "Check entries"])

            if action == "Add an entry":
                form_add = st.form(key="Add an entry")
                text_add = form_add.text_input(label="Type your text")
                submit = form_add.form_submit_button("Submit")

            if action == "Modify last entry":
                response = requests.get(f'http://host.docker.internal:8000/get_entry/{st.session_state["username"]}').json()
                form = st.form(key="Modify last entry")
                text_modify = form.text_input(label="Type your text", value=response)
                submit = form.form_submit_button("Submit")
            
            if action == "Check entries":
                form = st.form(key="Check entries")
                date = form.date_input(label="Choose a date")
                submit = form.form_submit_button("Submit")
                
            # ------------------------------------------Forms--------------------------------------------------
            if action !="":
                if submit:
                    if action == "Modify last entry":
                        response = requests.post('http://host.docker.internal:8000/modify_text', json= {
                            "text": text_modify,
                            "email": st.session_state["username"]
                        }).json()[0]
                        st.success(response)
                    elif action == "Add an entry":
                        response = requests.post('http://host.docker.internal:8000/add_text', json={
                            "text": text_add,
                            "email": st.session_state["username"]
                        }).json()[0]
                        st.success(response)
                    elif action == "Check entries":
                        response = requests.get(f'http://host.docker.internal:8000/get_entries/{st.session_state["username"]}/{date}').json()[0]
                        st.write(response)
            # --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    if st._is_running_with_streamlit:
        patients_name = get_all_patients_name()
        dates, date_min, date_max = get_dates()
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())