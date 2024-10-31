import streamlit as st
import sqlite3
import random
from datetime import datetime

# Initialize database connection
conn = sqlite3.connect('community_feed.db', check_same_thread=False)
c = conn.cursor()

# Database setup
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

# Helper functions for database operations
def add_post(content):
    username = f"User{random.randint(1000, 9999)}"  # Generate random username
    c.execute('INSERT INTO posts (content, username) VALUES (?, ?)', (content, username))
    conn.commit()

def get_posts():
    c.execute('SELECT id, content, created_at, likes, username FROM posts ORDER BY created_at DESC')
    return c.fetchall()

def add_like(post_id):
    c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
    conn.commit()

def get_confessions():
    # Placeholder for confessions, can be added to a separate table
    return ["I once spilled coffee on my boss's laptop.", "I never wash my hands after using public restrooms."]

# Streamlit app layout
st.set_page_config(page_title="Community Feed", page_icon="🌐", layout="wide")
st.title("🌐 Anonymous Community Feed")

# Add CSS for custom styling
st.markdown("""
    <style>
    .post-content {
        padding: 10px;
        border-radius: 8px;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .mystery-like {
        animation: bounce 0.5s infinite;
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    </style>
    """, unsafe_allow_html=True)

# Form for creating new posts
st.sidebar.header("📝 Share Something")
with st.sidebar.form(key="post_form"):
    post_content = st.text_area("What's on your mind?", max_chars=280)
    submit_button = st.form_submit_button("Post")
    if submit_button and post_content:
        add_post(post_content)
        st.sidebar.success("🎉 Your post has been shared!")
        st.experimental_rerun()

# Display posts in the community feed
st.subheader("📢 Community Feed")
posts = get_posts()

if posts:
    for post_id, content, created_at, likes, username in posts:
        st.markdown(f"<div class='post-content'><strong>{username}:</strong> {content}</div>", unsafe_allow_html=True)
        st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")

        # Mystery Likes
        if st.button(f"👻 Mystery Like ({likes})", key=f"like_{post_id}"):
            add_like(post_id)
            st.markdown("<div class='mystery-like'>✨ Someone liked this!</div>", unsafe_allow_html=True)
            st.experimental_rerun()

        st.write("---")

else:
    st.info("No posts yet. Be the first to share!")

# Confession Box
st.subheader("🤫 Confession Box")
if st.button("Reveal a Confession"):
    confessions = get_confessions()
    confession = random.choice(confessions)
    st.write(f"**Confession:** {confession}")

# Random Post Reveal
if st.button("🔍 Reveal a Random Post"):
    random_post = random.choice(posts)
    post_id, content, created_at, likes, username = random_post
    st.markdown(f"<div class='post-content'><strong>{username}:</strong> {content}</div>", unsafe_allow_html=True)
    st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")
else:
    st.info("Press the button to reveal a random post!")
