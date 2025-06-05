import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from datetime import datetime as dt
import json
import os
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="🏦 Customer Churn Prediction",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fbff 0%, #f0f7ff 100%);
        min-height: 100vh;
    }
    
    .main-header {
        background: rgba(255,255,255,0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 25px rgba(42,74,124,0.08);
        margin: 1rem 0;
        border: 1px solid rgba(42,74,124,0.1);
    }
    
    .prediction-card {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 4px 25px rgba(42,74,124,0.08);
        margin: 2rem 0;
        border: 1px solid rgba(42,74,124,0.1);
        text-align: center;
    }
    
    .styled-form {
        background: rgba(255,255,255,0.95) !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        box-shadow: 0 4px 25px rgba(42,74,124,0.05) !important;
        border: 1px solid rgba(42,74,124,0.05);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        padding: 0 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.7) !important;
        border-radius: 15px !important;
        padding: 1rem 2rem !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(42,74,124,0.1) !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #2a4a7c !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(42,74,124,0.15) !important;
    }
    
    .stButton button {
        background: #2a4a7c !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(42,74,124,0.2) !important;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2a4a7c 0%, #1a3357 100%) !important;
        color: white;
        padding: 1.5rem;
    }
    
    .user-card {
        background: rgba(255,255,255,0.15);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    .file-uploader {
        border: 2px dashed #2a4a7c !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        background: rgba(42,74,124,0.05) !important;
    }
    
    .churn-risk {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .low-risk {
        color: #2ecc71;
    }
    
    .high-risk {
        color: #e74c3c;
    }
    </style>
""", unsafe_allow_html=True)

# User Authentication Functions
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

def register_user(username, password, email, company, role, experience):
    users = load_users()
    if any(user['email'] == email for user in users):
        return False, "Email already registered"
    users.append({
        'username': username,
        'password': password,
        'email': email,
        'company': company,
        'role': role,
        'experience': experience
    })
    save_users(users)
    return True, "Registration successful"

def login_user(email, password):
    users = load_users()
    for user in users:
        if user['email'] == email and user['password'] == password:
            return True, user
    return False, None

# Session State Management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# App Components
@st.cache_resource
def load_model():
    return joblib.load("churn_prediction.pkl")

@st.cache_data
def load_original_data():
    return pd.read_csv("Churn_Modelling.csv")

def login_page():
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("login_form"):
                st.markdown("""
                    <div style='text-align: center; margin-bottom: 2.5rem;'>
                        <h1 style='color: #2a4a7c; margin-bottom: 0.5rem;'>🏦 Churn Analytics</h1>
                        <p style='color: #666;'>Customer Retention Prediction Platform</p>
                    </div>
                """, unsafe_allow_html=True)
                
                email = st.text_input("Email", placeholder="Enter your work email")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if submitted:
                    if not email or not password:
                        st.warning("Please fill in all fields")
                        return
                    success, user = login_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

def registration_page():
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("""
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <h2 style='color: #2a4a7c;'>Create Account</h2>
                    <p style='color: #666;'>Get started with your free trial</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("register_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    username = st.text_input("Full Name", placeholder="John Doe")
                    company = st.text_input("Organization", placeholder="Company Name")
                    role = st.selectbox("Role", ["Analyst", "Manager", "Director", "Executive"])
                with col_b:
                    email = st.text_input("Work Email", placeholder="john@company.com")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    experience = st.selectbox("Experience", ["0-2 years", "3-5 years", "6-10 years", "10+ years"])
                
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    if not all([username, email, password, company]):
                        st.error("All fields are required")
                    else:
                        success, message = register_user(username, password, email, company, role, experience)
                        if success:
                            st.success("Account created! Please sign in")
                        else:
                            st.error(message)

def prediction_form():
    original_data = load_original_data()
    with st.form("prediction_form"):
        st.markdown('<div class="styled-form">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Customer Demographics")
            geography = st.selectbox("Geography", original_data['Geography'].unique())
            gender = st.selectbox("Gender", original_data['Gender'].unique())
            age = st.slider("Age", min_value=18, max_value=100, value=40)
            
        with col2:
            st.subheader("Financial Details")
            credit_score = st.slider("Credit Score", min_value=300, max_value=850, value=650)
            balance = st.number_input("Balance", min_value=0.0, max_value=300000.0, value=50000.0)
            estimated_salary = st.number_input("Estimated Salary", min_value=0.0, max_value=300000.0, value=75000.0)
            
        with col3:
            st.subheader("Product Engagement")
            tenure = st.slider("Tenure (years)", min_value=0, max_value=10, value=5)
            num_of_products = st.selectbox("Number of Products", [1, 2, 3, 4])
            has_cr_card = st.selectbox("Has Credit Card", ["Yes", "No"])
            is_active_member = st.selectbox("Is Active Member", ["Yes", "No"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        if st.form_submit_button("Predict Churn Risk", use_container_width=True):
            # Convert inputs to model format
            has_cr_card = 1 if has_cr_card == "Yes" else 0
            is_active_member = 1 if is_active_member == "Yes" else 0
            
            return pd.DataFrame([{
                'Geography': geography,
                'Gender': gender,
                'Age': age,
                'CreditScore': credit_score,
                'Balance': balance,
                'EstimatedSalary': estimated_salary,
                'Tenure': tenure,
                'NumOfProducts': num_of_products,
                'HasCrCard': has_cr_card,
                'IsActiveMember': is_active_member
            }])
    return None

def churn_prediction_page():
    model = load_model()
    
    st.markdown(f"""
        <div class="main-header">
            <div style="display: flex; align-items: center; gap: 1.5rem; padding: 1rem;">
                <span style="font-size: 3rem;">🏦</span>
                <div>
                    <h1 style="color: #2a4a7c; margin: 0;">Customer Churn Prediction</h1>
                    <p style="margin: 0.2rem 0 0; color: #666;">Welcome back, {st.session_state.user_info['username']}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 Single Prediction", "📊 Batch Analysis"])
    
    with tab1:
        input_data = prediction_form()
        if input_data is not None:
            with st.spinner('Analyzing customer data...'):
                # Get probability and prediction
                proba = model.predict_proba(input_data)[0][1]
                prediction = model.predict(input_data)[0]
                
                risk_level = "High Risk" if prediction == 1 else "Low Risk"
                risk_color = "high-risk" if prediction == 1 else "low-risk"
                
                st.markdown(f"""
                    <div class="prediction-card">
                        <h3 style="color: #666; margin-bottom: 1.5rem;">CHURN RISK PREDICTION</h3>
                        <div class="churn-risk {risk_color}">
                            {'⚠️' if prediction == 1 else '✅'} {risk_level}
                        </div>
                        <div style="font-size: 1.5rem; margin: 1rem 0;">
                            Probability: {proba*100:.1f}%
                        </div>
                        <div style="height: 4px; background: {'#e74c3c' if prediction == 1 else '#2ecc71'}; 
                             width: 40%; margin: 0 auto; opacity: 0.3; border-radius: 2px;"></div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show feature importance explanation
                st.markdown("### Key Factors Influencing This Prediction")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                        - **Age**: Older customers are more likely to churn
                        - **Activity Status**: Inactive members have higher churn risk
                        - **Number of Products**: Customers with more products may be more likely to leave
                    """)
                
                with col2:
                    st.markdown("""
                        - **Geography**: Customers from certain regions have higher churn rates
                        - **Gender**: Female customers tend to churn more often
                        - **Balance**: Customers with extreme balance values may be at risk
                    """)
    
    with tab2:
        with st.container():
            st.markdown("""
                <div style="background: white; border-radius: 20px; padding: 2rem; margin: 1rem 0;">
                    <h3 style="color: #2a4a7c;">Bulk Churn Analysis</h3>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("Upload customer dataset", type=["xlsx", "csv"], 
                                           label_visibility="collapsed")
            if uploaded_file:
                try:
                    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
                    st.success("Dataset successfully loaded")
                    
                    required_columns = ['Geography', 'Gender', 'Age', 'CreditScore', 'Balance', 
                                      'EstimatedSalary', 'Tenure', 'NumOfProducts', 'HasCrCard', 'IsActiveMember']
                    
                    if not all(col in df.columns for col in required_columns):
                        st.error(f"Uploaded file must contain these columns: {', '.join(required_columns)}")
                    else:
                        if st.button("Run Churn Analysis", use_container_width=True):
                            with st.spinner('Processing customer data...'):
                                predictions = model.predict(df)
                                probabilities = model.predict_proba(df)[:, 1]
                                results = df.copy()
                                results["Churn_Prediction"] = predictions
                                results["Churn_Probability"] = probabilities
                                st.session_state.results = results
                    
                    if "results" in st.session_state:
                        st.download_button("Export Results", 
                                         st.session_state.results.to_csv(index=False),
                                         "churn_predictions.csv", "text/csv",
                                         use_container_width=True)
                        
                        with st.expander("Advanced Analytics"):
                            col1, col2 = st.columns(2)
                            with col1:
                                fig = px.pie(st.session_state.results, 
                                           names="Churn_Prediction",
                                           title="Churn Distribution",
                                           labels={'0': 'Retained', '1': 'Churned'})
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                fig = px.histogram(st.session_state.results, 
                                                x="Churn_Probability",
                                                nbins=20,
                                                title="Churn Probability Distribution")
                                st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown("### High-Risk Customers")
                            high_risk = st.session_state.results[st.session_state.results['Churn_Prediction'] == 1]
                            st.dataframe(high_risk.sort_values("Churn_Probability", ascending=False).head(10))
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
            
            st.markdown("</div>", unsafe_allow_html=True)

def main():
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Register"])
        with tab1:
            login_page()
        with tab2:
            registration_page()
    else:
        churn_prediction_page()
        
        # Sidebar Management
        with st.sidebar:
            st.markdown(f"""
                <div class="user-card">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                        <div style="font-size: 1.5rem;">👤</div>
                        <div>
                            <h4 style="margin: 0; color: white;">{st.session_state.user_info['username']}</h4>
                            <p style="margin: 0; font-size: 0.9rem; color: rgba(255,255,255,0.8);">
                                {st.session_state.user_info['role']}
                            </p>
                        </div>
                    </div>
                    <p style="margin: 0;"><strong>Organization:</strong> {st.session_state.user_info['company']}</p>
                    <p style="margin: 0;"><strong>Experience:</strong> {st.session_state.user_info['experience']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Model Information")
            st.markdown("""
                **Algorithm:** Gradient Boosting Classifier
                \n**Accuracy:** 86.4%
                \n**Recall:** 86.4%
                \n**F1-Score:** 85.2%
            """)
            
            if st.button("🚪 Log Out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.rerun()

if __name__ == "__main__":
    main()