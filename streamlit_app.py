import streamlit as st
import sqlite3
import random
from datetime import datetime

# Initialize database connection
conn = sqlite3.connect('community_feed.db', check_same_thread=False)
c = conn.cursor()

# Reset database schema for development
c.execute('DROP TABLE IF EXISTS posts')
c.execute('DROP TABLE IF EXISTS comments')
c.execute('DROP TABLE IF EXISTS polls')

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

c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS polls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        votes_a INTEGER DEFAULT 0,
        votes_b INTEGER DEFAULT 0
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

def add_like(post_id):
    c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
    conn.commit()

def add_poll(question, option_a, option_b):
    c.execute('INSERT INTO polls (question, option_a, option_b) VALUES (?, ?, ?)', (question, option_a, option_b))
    conn.commit()

def get_polls():
    c.execute('SELECT id, question, option_a, option_b, votes_a, votes_b FROM polls')
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
        st.experimental_rerun()

# Poll Creation
st.sidebar.header("📊 Create a Poll")
with st.sidebar.form(key="poll_form"):
    poll_question = st.text_input("Poll Question")
    option_a = st.text_input("Option A")
    option_b = st.text_input("Option B")
    submit_poll_button = st.form_submit_button("Create Poll")
    if submit_poll_button and poll_question and option_a and option_b:
        add_poll(poll_question, option_a, option_b)
        st.sidebar.success("🗳️ Your poll has been created!")
        st.experimental_rerun()

# Display posts
st.subheader("📢 Community Feed")
posts = get_posts()

if posts:
    for post_id, content, created_at, likes, username in posts:
        st.markdown(f"<div class='post-content'><strong>{username}:</strong> {content}</div>", unsafe_allow_html=True)
        st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")

        if st.button(f"👻 Mystery Like ({likes})", key=f"like_{post_id}"):
            add_like(post_id)
            st.markdown("<div class='mystery-like'>✨ Someone liked this!</div>", unsafe_allow_html=True)
            st.experimental_rerun()

        st.write("---")

else:
    st.info("No posts yet. Be the first to share!")

# Display polls
st.subheader("📊 Community Polls")
polls = get_polls()
for poll_id, question, option_a, option_b, votes_a, votes_b in polls:
    st.write(f"**{question}**")
    st.write(f"1️⃣ {option_a} - {votes_a} Votes")
    st.write(f"2️⃣ {option_b} - {votes_b} Votes")
    vote_option = st.radio("Choose an option:", (option_a, option_b), key=f"poll_{poll_id}")
    if st.button("Vote", key=f"vote_{poll_id}"):
        if vote_option == option_a:
            c.execute('UPDATE polls SET votes_a = votes_a + 1 WHERE id = ?', (poll_id,))
        else:
            c.execute('UPDATE polls SET votes_b = votes_b + 1 WHERE id = ?', (poll_id,))
        conn.commit()
        st.success("✅ Your vote has been recorded!")
        st.experimental_rerun()

# Additional fun features
st.subheader("📖 Story Time")
story = st.text_area("Share your short story anonymously...")
if st.button("Share Story"):
    if story:
        add_post(story)
        st.success("📚 Your story has been shared!")
        st.experimental_rerun()

st.subheader("🔊 Whisper Mode")
whisper_message = st.text_input("Send an anonymous message to someone...")
if st.button("Send Whisper"):
    if whisper_message:
        st.success("📩 Your whisper has been sent anonymously!")
        st.experimental_rerun()
