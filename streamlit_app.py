import streamlit as st
import sqlite3
from datetime import datetime

# Initialize or connect to the SQLite database
def init_db():
    conn = sqlite3.connect('community_feed.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0
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
    return conn, c

# Initialize database connection and cursor
conn, c = init_db()

# Helper functions for database operations
def add_post(content):
    c.execute('INSERT INTO posts (content) VALUES (?)', (content,))
    conn.commit()

def get_posts():
    c.execute('SELECT id, content, created_at, likes FROM posts ORDER BY created_at DESC')
    return c.fetchall()

def add_like(post_id):
    c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
    conn.commit()

def add_comment(post_id, content):
    c.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (post_id, content))
    conn.commit()

def get_comments(post_id):
    c.execute('SELECT content, created_at FROM comments WHERE post_id = ? ORDER BY created_at ASC', (post_id,))
    return c.fetchall()

# Streamlit app layout
st.title("🌐 Anonymous Community Feed")

# Form for creating new posts
st.sidebar.header("📝 Share Something")
with st.sidebar.form(key="post_form"):
    post_content = st.text_area("What's on your mind?", max_chars=280)
    submit_button = st.form_submit_button("Post")
    if submit_button and post_content:
        add_post(post_content)
        st.sidebar.success("🎉 Your post has been shared!")
        st.experimental_rerun()

# Display all posts in the community feed
st.subheader("📢 Community Feed")
posts = get_posts()

if posts:
    for post_id, content, created_at, likes in posts:
        st.markdown(f"**{content}**")
        st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")

        # Like button with a counter
        if st.button(f"👍 {likes}", key=f"like_{post_id}"):
            add_like(post_id)
            st.experimental_rerun()

        # Comments section with an expandable view
        with st.expander("💬 View Comments"):
            comments = get_comments(post_id)
            for comment_content, comment_date in comments:
                st.write(f"{comment_content} - *{comment_date}*")

            # Comment input
            comment_text = st.text_input(f"Add a comment for post {post_id}", key=f"comment_{post_id}")
            if st.button("Submit Comment", key=f"submit_comment_{post_id}") and comment_text:
                add_comment(post_id, comment_text)
                st.experimental_rerun()

        st.write("---")
else:
    st.info("No posts yet. Be the first to share!")
