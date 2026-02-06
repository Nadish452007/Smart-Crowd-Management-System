import streamlit as st
from auth import create_user, login_user
import cv2
import tempfile
import numpy as np
import os
import base64
from ultralytics import YOLO

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Crowd Management System",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# --- LOAD BACKGROUND IMAGE ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


background_image_file = "background.jpg"

if os.path.exists(background_image_file):
    bin_str = get_base64_of_bin_file(background_image_file)
    background_css = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.8)), url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """
else:
    background_css = """
        <style>
        .stApp { background: linear-gradient(135deg, #141e30, #243b55); }
        </style>
    """

st.markdown(background_css, unsafe_allow_html=True)

# --- CUSTOM CSS ---
st.markdown("""
<style>
/* Hide the default Streamlit header and footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Force Text Color to White */
h1, h2, h3, p, label {
    color: white !important;
    text-align: center !important;
}

/* Style the Inputs (Dark transparent look) */
div[data-baseweb="input"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    color: white;
}
div[data-baseweb="input"] > div {
    color: white !important; /* Text inside input */
    background-color: transparent !important;
}

/* Center the Main Content Column */
.block-container {
    max-width: 500px;
    padding-top: 5rem;
}

/* Gradient Button Style */
.stButton>button {
    width: 100%;
    border-radius: 25px;
    border: none;
    color: white;
    font-weight: bold;
    font-size: 18px;
    padding: 12px 0;
    margin-top: 10px;
    background: linear-gradient(90deg, #00c6ff, #ff00cc);
    box-shadow: 0px 4px 15px rgba(0, 198, 255, 0.4);
}
.stButton>button:hover {
    box-shadow: 0px 6px 20px rgba(0, 198, 255, 0.6);
    color: white;
}

/* Status Box Styles (For Dashboard) */
.status-box {
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: white;
    margin-top: 10px;
    border: 2px solid rgba(255,255,255,0.2);
}
.safe { background-color: #2ecc71; }
.medium { background-color: #f1c40f; color: black; }
.high { background-color: #e67e22; }
.danger { background-color: #e74c3c; animation: pulse 1s infinite; }

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}
</style>
""", unsafe_allow_html=True)

# --- AUTH LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


def toggle_auth_mode():
    if st.session_state.auth_mode == "login":
        st.session_state.auth_mode = "signup"
    else:
        st.session_state.auth_mode = "login"


# --- MAIN APP ---
if not st.session_state.logged_in:

    if st.session_state.auth_mode == "login":
        st.markdown("<h1>Login</h1>", unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Type your username", key="login_user",
                                 label_visibility="visible")
        password = st.text_input("Password", type="password", placeholder="Type your password", key="login_pass",
                                 label_visibility="visible")

        st.markdown("###")  # Spacer

        if st.button("LOGIN"):
            result = login_user(username, password)
            if result:
                st.session_state.logged_in = True
                st.session_state.user = result[0]
                st.session_state.role = result[2]
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown("---")
        st.markdown("<p style='font-size:14px; color:#ddd;'>Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("Sign Up Here"):
            toggle_auth_mode()
            st.rerun()

    else:  # SIGNUP MODE
        st.markdown("<h1>Sign Up</h1>", unsafe_allow_html=True)

        new_user = st.text_input("New Username", placeholder="Create a username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", placeholder="Create a password", key="signup_pass")
        role = st.selectbox("Role", ["user", "admin"], key="signup_role")

        st.markdown("###")  # Spacer

        if st.button("CREATE ACCOUNT"):
            if create_user(new_user, new_pass, role):
                st.success("Account created! Please Login.")
                st.session_state.auth_mode = "login"
                st.rerun()
            else:
                st.error("User already exists")

        st.markdown("---")
        st.markdown("<p style='font-size:14px; color:#ddd;'>Already have an account?</p>", unsafe_allow_html=True)
        if st.button("Login Here"):
            toggle_auth_mode()
            st.rerun()

else:
    # --- DASHBOARD (LOGGED IN) ---
    with st.sidebar:
        st.success(f"User: {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # --- CHANGED TITLE HERE ---
    st.title("Smart Crowd Management System")


    @st.cache_resource
    def load_model():
        return YOLO('yolov8m.pt')


    model = load_model()

    uploaded_file = st.file_uploader("Upload Surveillance Feed", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)

        frame_window = st.image([])
        status_placeholder = st.empty()

        LIMIT_SAFE = 5
        LIMIT_MEDIUM = 10
        LIMIT_HIGH = 15

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            results = model.track(frame, persist=True, conf=0.15, iou=0.8, imgsz=1280, classes=0,
                                  tracker="bytetrack.yaml", verbose=False)
            res_plotted = results[0].plot()
            person_count = len(results[0].boxes)

            if person_count <= LIMIT_SAFE:
                status_html = f'<div class="status-box safe">🟢 SAFE (Count: {person_count})</div>'
                color = (0, 255, 0)
            elif person_count <= LIMIT_MEDIUM:
                status_html = f'<div class="status-box medium">🟡 MEDIUM (Count: {person_count})</div>'
                color = (0, 255, 255)
            elif person_count <= LIMIT_HIGH:
                status_html = f'<div class="status-box high">🟠 HIGH (Count: {person_count})</div>'
                color = (0, 165, 255)
            else:
                status_html = f'<div class="status-box danger">🔴 DANGER (Count: {person_count})</div>'
                color = (0, 0, 255)

            status_placeholder.markdown(status_html, unsafe_allow_html=True)
            cv2.putText(res_plotted, f"Count: {person_count}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

            res_plotted = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
            frame_window.image(res_plotted)

        cap.release()