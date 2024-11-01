import streamlit as st
import sqlite3
import random

# Initialize database connection
def init_db():
    try:
        conn = sqlite3.connect('community_feed.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            username TEXT NOT NULL
        )
        ''')
        conn.commit()
        return conn, c
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None, None

conn, c = init_db()

# Helper functions
def random_nickname():
    nicknames = ["Mysterious Dolphin", "Sneaky Ninja", "Curious Cat", "Wandering Wizard", "Clever Fox"]
    return random.choice(nicknames)

def add_post(content):
    try:
        username = random_nickname()
        c.execute('INSERT INTO posts (content, username) VALUES (?, ?)', (content, username))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error adding post: {e}")

def get_posts():
    try:
        c.execute('SELECT id, content, created_at, likes, username FROM posts ORDER BY created_at DESC')
        return c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error retrieving posts: {e}")
        return []

def add_like(post_id):
    try:
        c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error adding like: {e}")

# Streamlit app layout
st.set_page_config(page_title="Anonymous Community Feed", page_icon="🌐", layout="wide")
st.title("🌐 Anonymous Community Feed")

# Sidebar for creating posts
st.sidebar.header("📝 Share Something")
post_content = st.sidebar.text_area("What's on your mind?", max_chars=280)
submit_button = st.sidebar.button("Post")

if submit_button and post_content:
    add_post(post_content)
    st.sidebar.success("🎉 Your post has been shared!")

# Display posts
st.subheader("📢 Community Feed")
posts = get_posts()

if posts:
    for post_id, content, created_at, likes, username in posts:
        st.markdown(f"<div style='padding: 10px; border: 1px solid #ddd; margin-bottom: 10px;'><strong>{username}:</strong> {content}</div>", unsafe_allow_html=True)
        st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")

        if st.button(f"👻 Like ({likes})", key=f"like_{post_id}"):
            add_like(post_id)
            st.success("✨ Someone liked this!")
else:
    st.info("No posts yet. Be the first to share!")

# Close the database connection when done
if conn:
    conn.close()
