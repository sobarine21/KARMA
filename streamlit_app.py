import streamlit as st
import sqlite3
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
        likes INTEGER DEFAULT 0
    )
''')

# Check if 'likes' column exists and add it if missing
try:
    c.execute('SELECT likes FROM posts LIMIT 1')
except sqlite3.OperationalError:
    c.execute('ALTER TABLE posts ADD COLUMN likes INTEGER DEFAULT 0')
    conn.commit()

c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

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

def get_top_posts(limit=5):
    c.execute('SELECT id, content, created_at, likes FROM posts ORDER BY likes DESC LIMIT ?', (limit,))
    return c.fetchall()

def delete_post(post_id):
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    c.execute('DELETE FROM comments WHERE post_id = ?', (post_id,))
    conn.commit()

def search_posts(keyword):
    keyword = f"%{keyword}%"
    c.execute('SELECT id, content, created_at, likes FROM posts WHERE content LIKE ? ORDER BY created_at DESC', (keyword,))
    return c.fetchall()

# Streamlit app layout
st.set_page_config(page_title="Community Feed", page_icon="🌐", layout="wide")
st.title("🌐 Anonymous Community Feed")

# Add some CSS for custom styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .post-content {
        padding: 10px;
        border-radius: 8px;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .post-content:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .comment-content {
        padding: 5px;
        border-radius: 5px;
        background-color: #e8e8e8;
    }
    .likes-button {
        margin-right: 10px;
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

# Search Bar
st.subheader("🔍 Search Posts")
search_query = st.text_input("Enter keyword to search...")
if search_query:
    search_results = search_posts(search_query)
    if search_results:
        st.write(f"**Results for '{search_query}':**")
        for post_id, content, created_at, likes in search_results:
            st.markdown(f"**{content}**")
            st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")
            st.write("---")
    else:
        st.warning("No results found!")

# Display top posts based on likes
st.subheader("🔥 Top Posts")
top_posts = get_top_posts()
if top_posts:
    for post_id, content, created_at, likes in top_posts:
        st.markdown(f"**{content}**")
        st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")
        st.write("---")

# Display all posts in the community feed
st.subheader("📢 Community Feed")
posts = get_posts()

if posts:
    for post_id, content, created_at, likes in posts:
        # Display post content and created date
        st.markdown(f"<div class='post-content'><strong>{content}</strong></div>", unsafe_allow_html=True)
        st.write(f"📅 *Posted on {created_at}*")

        # Like button with a counter
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            if st.button(f"👍 {likes}", key=f"like_{post_id}"):
                add_like(post_id)
                st.experimental_rerun()

        # Comments section with an expandable view
        with st.expander("💬 View Comments", expanded=False):
            comments = get_comments(post_id)
            for comment_content, comment_date in comments:
                st.markdown(f"<div class='comment-content'>{comment_content} - <i>{comment_date}</i></div>", unsafe_allow_html=True)

            # Comment input
            comment_text = st.text_input(f"Add a comment for post {post_id}", key=f"comment_{post_id}")
            if st.button("Submit Comment", key=f"submit_comment_{post_id}") and comment_text:
                add_comment(post_id, comment_text)
                st.experimental_rerun()

        # Optional: Add a delete button for testing purposes
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{post_id}"):
                delete_post(post_id)
                st.experimental_rerun()

        st.write("---")
else:
    st.info("No posts yet. Be the first to share!")
