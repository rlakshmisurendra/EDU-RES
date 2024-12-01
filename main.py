import os
import sqlite3
import streamlit as st

# Constants
DATABASE_PATH = "resources.db"
UPLOAD_DIR = "uploads"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            path TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Insert a new resource into the database
def insert_resource(name, category, path):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO resources (name, category, path) VALUES (?, ?, ?)", (name, category, path))
    conn.commit()
    conn.close()

# Fetch all unique categories
def get_categories():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM resources")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

# Fetch resources by category
def get_resources_by_category(category):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, path FROM resources WHERE category = ?", (category,))
    resources = cursor.fetchall()
    conn.close()
    return resources

# Delete a specific file
def delete_file(file_name, file_path):
    try:
        # Remove the file from the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resources WHERE name = ?", (file_name,))
        conn.commit()
        conn.close()

        # Remove the file from local storage
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        st.error(f"An error occurred while deleting the file: {e}")

# Delete an entire category
def delete_category(category_name):
    try:
        # Get all files in the category
        resources = get_resources_by_category(category_name)

        # Remove each file from local storage
        for _, file_path in resources:
            if os.path.exists(file_path):
                os.remove(file_path)

        # Remove the category and all associated files from the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resources WHERE category = ?", (category_name,))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"An error occurred while deleting the category: {e}")

# Admin Page
def admin_page():
    st.title("AMDIN'S !!")
    st.subheader("Upload Resources")

    # File upload section
    file = st.file_uploader("Choose a file", type=["pdf", "docx", "pptx", "txt"])
    category = st.text_input("Enter subject ")
    if st.button("Upload"):
        if file and category:
            # Save the file locally
            file_path = os.path.join(UPLOAD_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # Insert file metadata into SQLite database
            insert_resource(file.name, category, file_path)

            st.success(f"File '{file.name}' uploaded successfully under '{category}'!")
        else:
            st.error("Please provide both a file and a subject.")

    st.subheader("Delete Files")

    # Fetch categories
    categories = get_categories()
    if categories:
        # Dropdown to select a category
        selected_category = st.selectbox("Select a subject to manage", ["Select"] + categories)

        if selected_category != "Select":
            # List all resources in the selected category
            st.markdown(f"### Files in {selected_category}")
            resources = get_resources_by_category(selected_category)

            if not resources:
                st.info(f"No resources found in '{selected_category}'.")
            else:
                for resource in resources:
                    file_name, file_path = resource
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(file_name)  # Display file name
                    with col2:
                        # Delete file button
                        if st.button(f"Delete", key=f"delete_{file_name}"):
                            delete_file(file_name, file_path)
                            st.success(f"File '{file_name}' deleted successfully.")
                            st.experimental_rerun()

            # Option to delete entire category
            if st.button(f"Delete all files of '{selected_category}'"):
                delete_category(selected_category)
                st.success(f"Category '{selected_category}' and all its files deleted successfully.")
                st.experimental_rerun()
    else:
        st.info("No categories available to delete.")

    # Admin Logout Button
    if st.button("Logout"):
        st.session_state.page = "login"
        st.session_state.authenticated = False
        st.session_state.role = None
        st.experimental_rerun()

# User Page
def user_page():
    st.title("SEMESTER 3 - 2 ")

    # Fetch and display categories
    categories = get_categories()
    if categories:
        for category in categories:
            with st.expander(f"Subject : {category}"):
                resources = get_resources_by_category(category)
                if not resources:
                    st.write("No files available in this category.")
                else:
                    for file_name, file_path in resources:
                        col1, col2 = st.columns([6, 1])
                        with col1:
                            st.write(file_name)  # Display the file name
                        with col2:
                            # Download button
                            if st.download_button(f"Download ", open(file_path, "rb"), file_name):
                                st.success(f" downloaded !")
    else:
        st.info("No Subjects available.")

    # User Logout Button
    if st.button("Logout"):
        st.session_state.page = "login"
        st.session_state.authenticated = False
        st.session_state.role = None
        st.experimental_rerun()

# Login Page
def login_page():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check if the username matches the admin credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.page = "admin"
            st.session_state.authenticated = True
            st.session_state.role = "admin"
            st.experimental_rerun()

        # Check if the username is within the allowed student ranges
        elif (username.startswith("22F01A42") and 1 <= int(username[8:10]) <= 66) or \
             (username.startswith("23F05A42") and 1 <= int(username[8:10]) <= 7):
            if password == username:
                st.session_state.page = "user"
                st.session_state.authenticated = True
                st.session_state.role = "user"
                st.experimental_rerun()
            else:
                st.error("Invalid password!")
        else:
            st.error("Invalid credentials!")

# Main
def main():
    # Initialize session state variables
    if "page" not in st.session_state:
        st.session_state.page = "login"
        st.session_state.authenticated = False
        st.session_state.role = None

    # Page routing
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "admin":
        admin_page()
    elif st.session_state.page == "user":
        user_page()

if __name__ == "__main__":
    init_db()
    main()
