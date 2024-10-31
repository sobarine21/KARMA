import streamlit as st
import sqlite3
import random

# Initialize database connection
conn = sqlite3.connect('community_feed.db', check_same_thread=False)
c = conn.cursor()

# Database setup (reset for testing)
c.execute('DROP TABLE IF EXISTS posts')
c.execute('DROP TABLE IF EXISTS comments')
c.execute('DROP TABLE IF EXISTS polls')
c.execute('DROP TABLE IF EXISTS confessions')

c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        likes INTEGER DEFAULT 0,
        username TEXT NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()

# Helper functions
def random_nickname():
    nicknames = ["Mysterious Dolphin", "Sneaky Ninja", "Curious Cat", "Wandering Wizard", "Clever Fox"]
    return random.choice(nicknames)

def add_post(content):
    username = random_nickname()
    c.execute('INSERT INTO posts (content, username) VALUES (?, ?)', (content, username))
    conn.commit()

def get_posts():
    c.execute('SELECT id, content, created_at, likes, username FROM posts ORDER BY created_at DESC')
    return c.fetchall()

# Streamlit app layout
st.set_page_config(page_title="Anonymous Community Feed", page_icon="🌐", layout="wide")
st.title("🌐 Anonymous Community Feed")

# Sidebar for creating posts
st.sidebar.header("📝 Share Something")
with st.sidebar.form(key="post_form"):
    post_content = st.text_area("What's on your mind?", max_chars=280)
    submit_button = st.form_submit_button("Post")
    if submit_button and post_content:
        add_post(post_content)
        st.sidebar.success("🎉 Your post has been shared!")
        st.rerun()  # Rerun to refresh the feed

# Display posts
st.subheader("📢 Community Feed")
posts = get_posts()

if posts:
    for post_id, content, created_at, likes, username in posts:
        st.markdown(f"<div style='padding: 10px; border: 1px solid #ddd; margin-bottom: 10px;'><strong>{username}:</strong> {content}</div>", unsafe_allow_html=True)
        st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")

        if st.button(f"👻 Mystery Like ({likes})", key=f"like_{post_id}"):
            c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
            conn.commit()
            st.success("✨ Someone liked this!")
            st.rerun()  # Refresh the feed

        st.write("---")
else:
    st.info("No posts yet. Be the first to share!")

