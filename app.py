import streamlit as st
from cryptography.fernet import Fernet
import hashlib
import base64

# ------------------------ Session Initialization ------------------------
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'authorized' not in st.session_state:
    st.session_state.authorized = True

# ------------------------ Utility Functions -----------------------------
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def generate_fernet_key(passkey):
    hashed = hashlib.sha256(passkey.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

def encrypt_text(text, passkey):
    key = generate_fernet_key(passkey)
    return Fernet(key).encrypt(text.encode()).decode()

def decrypt_text(encrypted_text, passkey):
    try:
        key = generate_fernet_key(passkey)
        return Fernet(key).decrypt(encrypted_text.encode()).decode()
    except:
        return None

# ------------------------ Login Page -----------------------------------
def login_page():
    st.title("🔐 Reauthorization Required")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.authorized = True
            st.session_state.attempts = 0
            st.success("Login successful! Return to home page.")
        else:
            st.error("Invalid credentials")

# ------------------------ Insert Data Page -----------------------------
def insert_data_page():
    st.header("📝 Store New Data")
    key = st.text_input("Enter a unique key for your data")
    text = st.text_area("Enter the text to store")
    passkey = st.text_input("Set a passkey", type="password")
    if st.button("Store"):
        if key and text and passkey:
            encrypted = encrypt_text(text, passkey)
            st.session_state.stored_data[key] = {
                "encrypted_text": encrypted,
                "passkey_hash": hash_passkey(passkey)
            }
            st.success("Data stored successfully!")
        else:
            st.warning("Please fill in all fields.")

# ------------------------ Retrieve Data Page ---------------------------
def retrieve_data_page():
    st.header("🔍 Retrieve Stored Data")
    key = st.text_input("Enter the data key")
    passkey = st.text_input("Enter your passkey", type="password")
    if st.button("Retrieve"):
        if key in st.session_state.stored_data:
            data_entry = st.session_state.stored_data[key]
            if hash_passkey(passkey) == data_entry["passkey_hash"]:
                decrypted = decrypt_text(data_entry["encrypted_text"], passkey)
                st.success("Data decrypted successfully!")
                st.code(decrypted)
                st.session_state.attempts = 0  # reset
            else:
                st.session_state.attempts += 1
                remaining = 3 - st.session_state.attempts
                st.error(f"Wrong passkey! {remaining} attempt(s) remaining.")
                if st.session_state.attempts >= 3:
                    st.session_state.authorized = False
        else:
            st.warning("No data found for this key.")

# ------------------------ Main App -------------------------------------
def main():
    st.title("🛡️ Secure Data Encryption System")
    if not st.session_state.authorized:
        login_page()
        return

    menu = ["Home", "Insert Data", "Retrieve Data"]
    choice = st.sidebar.selectbox("Navigate", menu)

    if choice == "Home":
        st.write("Welcome! Use the sidebar to insert or retrieve secure data.")
    elif choice == "Insert Data":
        insert_data_page()
    elif choice == "Retrieve Data":
        retrieve_data_page()

if __name__ == "__main__":
    main()
