import pandas as pd
import streamlit as st
import joblib
from sklearn.preprocessing import MinMaxScaler
import io

buffer = io.BytesIO()

# Session state to collect multiple students
def init_session():
    if "students_data" not in st.session_state:
        st.session_state.students_data = []

def data_preprocessing(data_input, single_data, n):
    df = pd.read_csv('data_filtered.csv').drop(columns=['Status'], axis=1)
    df = pd.concat([data_input, df])
    df = MinMaxScaler().fit_transform(df)
    return df[[n]] if single_data else df[0:n]

def model_predict(df):
    model = joblib.load('Hasil Pemodelan/Model_Random_Forest.pkl')
    return model.predict(df)

def color_mapping(value):
    return f"background-color: {'#d4edda' if value == 'Graduate' else '#f8d7da'}; color: {'green' if value == 'Graduate' else 'red'}"

def main():
    st.set_page_config(page_title='Dropout Predictor', layout='wide')
    st.title('🎓 Jaya Jaya Institute - Dropout Risk Predictor')
    st.markdown('---')
    init_session()

    gender_mapping = {'Male': 1, 'Female': 0}
    marital_status_mapping = {
        'Single': 1, 'Married': 2, 'Widower': 3, 'Divorced': 4,
        'Facto Union': 5, 'Legally Seperated': 6
    }
    application_mapping = {
        '1st Phase - General Contingent': 1,
        '1st Phase - Special Contingent (Azores Island)': 5,
        '1st Phase - Special Contingent (Madeira Island)': 16,
        '2nd Phase - General Contingent': 17,
        '3rd Phase - General Contingent': 18,
        'Ordinance No. 612/93': 2, 'Ordinance No. 854-B/99': 10,
        'Ordinance No. 533-A/99, Item B2 (Different Plan)': 26,
        'Ordinance No. 533-A/99, Item B3 (Other Institution)': 27,
        'International Student (Bachelor)': 15, 'Over 23 Years Old': 39,
        'Transfer': 42, 'Change of Course': 43, 'Holders of Other Higher Courses': 7,
        'Short Cycle Diploma Holders': 53, 'Technological Specialization Diploma Holders': 44,
        'Change of Institution/Course': 51, 'Change of Institution/Course (International)': 57,
    }

    st.header("🔎 Input Data for One Student")
    with st.form("single_form"):
        col1, col2, col3 = st.columns(3)
        gender = col1.radio("Gender", options=list(gender_mapping.keys()))
        age = col2.number_input("Age at Enrollment", min_value=17, max_value=70)
        marital_status = col3.selectbox("Marital Status", list(marital_status_mapping.keys()))

        col4, col5, col6 = st.columns(3)
        application_mode = col4.selectbox("Application Mode", list(application_mapping.keys()))
        prev_grade = col5.number_input("Previous Qualification Grade", 0, 200)
        admission_grade = col6.number_input("Admission Grade", 0, 200)

        col7, col8, col9, col10 = st.columns(4)
        scholarship = col7.checkbox("Scholarship")
        tuition = col8.checkbox("Tuition up to date")
        displaced = col9.checkbox("Displaced")
        debtor = col10.checkbox("Debtor")

        col11, col12, col13 = st.columns(3)
        u1_enrolled = col11.number_input("1st Sem Enrolled", 0, 26)
        u2_enrolled = col12.number_input("2nd Sem Enrolled", 0, 23)
        u2_eval = col13.number_input("2nd Sem Evaluations", 0, 33)

        col14, col15, col16 = st.columns(3)
        u1_approved = col14.number_input("1st Sem Approved", 0, 26)
        u2_approved = col15.number_input("2nd Sem Approved", 0, 20)
        u2_noeval = col16.number_input("2nd Sem No Evaluations", 0, 12)

        col17, col18 = st.columns(2)
        u1_grade = col17.number_input("1st Sem Grade", 0, 20)
        u2_grade = col18.number_input("2nd Sem Grade", 0, 20)

        add_btn, predict_btn = st.columns(2)
        add_clicked = add_btn.form_submit_button("➕ Add Student")
        predict_clicked = predict_btn.form_submit_button("🔍 Predict All")

        if add_clicked:
            st.session_state.students_data.append([
                marital_status_mapping[marital_status], application_mapping[application_mode],
                prev_grade, admission_grade, int(displaced), int(debtor), int(tuition),
                gender_mapping[gender], int(scholarship), age,
                u1_enrolled, u1_approved, u1_grade, u2_enrolled,
                u2_eval, u2_approved, u2_grade, u2_noeval
            ])
            st.success("Student added to batch list.")

    if st.session_state.students_data:
        st.subheader("📋 Current Student Data")
        columns = [
            'Marital_status', 'Application_mode', 'Previous_qualification_grade',
            'Admission_grade', 'Displaced', 'Debtor', 'Tuition_fees_up_to_date',
            'Gender', 'Scholarship_holder', 'Age_at_enrollment',
            'Curricular_units_1st_sem_enrolled', 'Curricular_units_1st_sem_approved',
            'Curricular_units_1st_sem_grade', 'Curricular_units_2nd_sem_enrolled',
            'Curricular_units_2nd_sem_evaluations', 'Curricular_units_2nd_sem_approved',
            'Curricular_units_2nd_sem_grade', 'Curricular_units_2nd_sem_without_evaluations']

        df = pd.DataFrame(st.session_state.students_data, columns=columns)
        st.dataframe(df)

        if predict_clicked:
            data_input = data_preprocessing(df, False, len(df))
            outputs = model_predict(data_input)
            statuses = ['Graduate' if pred == 1 else 'Dropout' for pred in outputs]
            df['Prediction Result'] = statuses
            st.subheader("🔮 Prediction Results")
            st.dataframe(df.style.applymap(color_mapping, subset=['Prediction Result']))

if __name__ == '__main__':
    main()