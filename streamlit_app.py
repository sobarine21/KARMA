import streamlit as st
import psycopg2
import os

# Load database credentials from environment variables
DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_HOST = os.environ['POSTGRES_HOST']
DATABASE_PORT = os.environ['POSTGRES_PORT']
DATABASE_NAME = os.environ['POSTGRES_DB']
DATABASE_USER = os.environ['POSTGRES_USER']
DATABASE_PASSWORD = os.environ['POSTGRES_PASSWORD']

# Establish database connection
conn = psycopg2.connect(
    dbname=DATABASE_NAME,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT
)

# Create cursor
cur = conn.cursor()

# Create table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        username TEXT,
        post TEXT
    )
""")

# Streamlit app
st.title("Anonymous Community Feed")

# Mystery names generator
def generate_mystery_name():
    adjectives = ["Bold", "Mysterious", "Silent", "Unknown", "Ghost"]
    nouns = ["User", "Poster", "Writer", "Voice", "Mind"]
    return f"{random.choice(adjectives)}_{random.choice(nouns)}"

# Initialize session state
if 'username' not in st.session_state:
    st.session_state.username = generate_mystery_name()

# Change mystery name
def change_username():
    st.session_state.username = generate_mystery_name()

st.button("Change Mystery Name", on_click=change_username)

# Display current mystery name
st.write(f"Your Mystery Name: {st.session_state.username}")

# Text input for new posts
new_post = st.text_input("Make a new post:")

# Submit new post
def submit_post():
    cur.execute("INSERT INTO posts VALUES (%s, %s)", (st.session_state.username, new_post))
    conn.commit()
    st.experimental_rerun()

if st.button("Post"):
    submit_post()

# Display community feed
st.header("Community Feed")
cur.execute("SELECT * FROM posts ORDER BY RANDOM()")
posts = cur.fetchall()
for post in posts:
    st.write(f"{post[0]}: {post[1]}")

# Close database connection
def close_connection():
    conn.close()

st.atexit(close_connection())
