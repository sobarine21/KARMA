import streamlit as st
import sqlite3
import random

# Initialize database connection
conn = sqlite3.connect('community_feed.db', check_same_thread=False)
c = conn.cursor()

# Database setup
def create_tables():
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                username TEXT NOT NULL,
                karma INTEGER DEFAULT 0
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

        c.execute('''
            CREATE TABLE IF NOT EXISTS confessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS mystery_box (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
    except Exception as e:
        st.error(f"Error creating tables: {e}")

create_tables()

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
    try:
        c.execute('UPDATE posts SET likes = likes + 1, karma = karma + 1 WHERE id = ?', (post_id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        st.error(f"Operational error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

def add_confession(content):
    c.execute('INSERT INTO confessions (content) VALUES (?)', (content,))
    conn.commit()

def get_confessions():
    c.execute('SELECT content, created_at FROM confessions ORDER BY created_at DESC')
    return c.fetchall()

def add_poll(question, option_a, option_b):
    c.execute('INSERT INTO polls (question, option_a, option_b) VALUES (?, ?, ?)', (question, option_a, option_b))
    conn.commit()

def get_polls():
    c.execute('SELECT id, question, option_a, option_b, votes_a, votes_b FROM polls')
    return c.fetchall()

def add_mystery_message(content):
    c.execute('INSERT INTO mystery_box (content) VALUES (?)', (content,))
    conn.commit()

def get_random_mystery():
    c.execute('SELECT content FROM mystery_box ORDER BY RANDOM() LIMIT 1')
    return c.fetchone()

def add_qa(question):
    c.execute('INSERT INTO qa (question) VALUES (?)', (question,))
    conn.commit()

def answer_qa(question_id, answer):
    c.execute('UPDATE qa SET answer = ? WHERE id = ?', (answer, question_id))
    conn.commit()

def get_qa():
    c.execute('SELECT id, question, answer FROM qa ORDER BY created_at DESC')
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

# Confession Box
st.sidebar.header("🤫 Confession Box")
with st.sidebar.form(key="confession_form"):
    confession_content = st.text_area("What's your secret?", max_chars=280)
    submit_confession_button = st.form_submit_button("Share Confession")
    if submit_confession_button and confession_content:
        add_confession(confession_content)
        st.sidebar.success("🤐 Your confession has been shared!")
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

# Mystery Box
st.sidebar.header("🎁 Mystery Box")
with st.sidebar.form(key="mystery_form"):
    mystery_content = st.text_area("Add a mystery message...", max_chars=280)
    submit_mystery_button = st.form_submit_button("Share Mystery Message")
    if submit_mystery_button and mystery_content:
        add_mystery_message(mystery_content)
        st.sidebar.success("🎉 Your mystery message has been added!")

if st.sidebar.button("Reveal a Mystery"):
    mystery = get_random_mystery()
    if mystery:
        st.sidebar.markdown(f"<div style='padding: 10px; border: 1px solid #ddd;'>{mystery[0]}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.info("No mystery messages yet.")

# Anonymous Q&A
st.sidebar.header("❓ Ask a Question")
with st.sidebar.form(key="qa_form"):
    qa_question = st.text_input("What's your question?")
    submit_qa_button = st.form_submit_button("Submit Question")
    if submit_qa_button and qa_question:
        add_qa(qa_question)
        st.sidebar.success("📝 Your question has been submitted!")

# Display posts
st.subheader("📢 Community Feed")
posts = get_posts()

if posts:
    for post_id, content, created_at, likes, username in posts:
        st.markdown(f"<div style='padding: 10px; border: 1px solid #ddd; margin-bottom: 10px;'><strong>{username}:</strong> {content}</div>", unsafe_allow_html=True)
        st.write(f"📅 *Posted on {created_at}* - 👍 {likes} Likes")

        if st.button(f"👻 Mystery Like ({likes})", key=f"like_{post_id}"):
            add_like(post_id)
            st.success("✨ Someone liked this!")
            st.experimental_rerun()

        # Comments section
        comment_text = st.text_input(f"Add a comment for post {post_id}", key=f"comment_{post_id}")
        if st.button("💬 Submit Comment", key=f"submit_comment_{post_id}"):
            if comment_text:
                c.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (post_id, comment_text))
                conn.commit()
                st.success("🗨️ Your comment has been added!")
                st.experimental_rerun()

        st.write("---")

else:
    st.info("No posts yet. Be the first to share!")

# Display Confessions
st.subheader("🤫 Confessions")
confessions = get_confessions()
if confessions:
    for content, created_at in confessions:
        st.markdown(f"<div style='padding: 10px; border: 1px solid #ddd; margin-bottom: 10px;'>{content}</div>", unsafe_allow_html=True)
        st.write(f"📅 *Confessed on {created_at}*")
else:
    st.info("No confessions yet. Be the first to share!")

# Display polls
st.subheader("📊 Community Polls")
polls = get_polls()
if polls:
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
else:
    st.info("No polls yet. Be the first to create one!")

# Display Q&A
st.subheader("❓ Community Q&A")
qa_list = get_qa()
if qa_list:
    for q_id, question, answer in qa_list:
        st.markdown(f"**Q:** {question}")
        if answer:
            st.markdown(f"**A:** {answer}")
        else:
            answer_text = st.text_input(f"Answer this question:", key=f"answer_{q_id}")
            if st.button("Submit Answer", key=f"submit_answer_{q_id}"):
                answer_qa(q_id, answer_text)
                st.success("✅ Your answer has been submitted!")
                st.experimental_rerun()
else:
    st.info("No questions yet. Be the first to ask!")

# Close the database connection when done
conn.close()
