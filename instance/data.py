import sqlite3
from datetime import datetime
from flask_bcrypt import Bcrypt
from datetime import datetime


# Create a Flask-Bcrypt instance
bcrypt = Bcrypt()

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# Function to hash a password using Flask-Bcrypt
def hash_password(password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed_password

# Mockup user data with 'about_me' and 'description'
user_data = [
    ('user1', 'user1@example.com', hash_password('123'), 
     'Hello, my name is user1. I like gaming.', 
     'Hi, I am user1. I am 20 years old and my interests include gaming and programming.'),

    ('user2', 'user2@example.com', hash_password('456'), 
     'Hi there, I am user2. I enjoy music.', 
     'Hello, I am user2. I am 25 years old and I am passionate about music and traveling.'),

    ('user3', 'user3@example.com', hash_password('789'), 
     'Greetings, user3 here. I love reading.', 
     'Hi, I am user3. I am 30 years old and my hobbies include reading and hiking in nature.')
]

# Adjusted Insert users query to include 'about_me' and 'description'
insert_user_query = """
INSERT INTO user (username, email, password, about_me, description) 
VALUES (?, ?, ?, ?, ?)
"""
cursor.executemany(insert_user_query, user_data)


# Mockup tag data
tag_data = [
    ('transmog'),
    ('pvp'),
    ('pve'),
    # Add more tags as needed
]

# Insert tags
insert_tag_query = "INSERT INTO tag (tag_name) VALUES (?)"
cursor.executemany(insert_tag_query, [(tag,) for tag in tag_data])

# Commit the changes to the database
conn.commit()

# Associate users with tags (assuming id's of users and tags are 1, 2, 3, etc.)
user_tag_data = [
    (1, 1),
    (1, 2),
    (2, 3),
    # Add more user-tag associations as needed
]

# Insert user-tag associations
insert_user_tag_query = "INSERT INTO user_tag (user_id, tag_id) VALUES (?, ?)"
cursor.executemany(insert_user_tag_query, user_tag_data)

# Mockup post data
post_data = [
    ('Post Title 1', 'This is the content of post 1.', 0, None, datetime.now(), 1),
    ('Post Title 2', 'This is the content of post 2.', 0, None, datetime.now(), 2),
    ('Post Title 3', 'This is the content of post 3.', 0, None, datetime.now(), 1),
    ('Post Title 4', 'This is the content of post 4.', 0, None, datetime.now(), 2),
    ('Post Title 5', 'This is the content of post 5.', 0, None, datetime.now(), 1),
    ('Post Title 6', 'This is the content of post 6.', 0, None, datetime.now(), 2),
    ('Post Title 7', 'This is the content of post 7.', 0, None, datetime.now(), 3),
    ('Post Title 8', 'This is the content of post 8.', 0, None, datetime.now(), 3),
]

# Adjusted Insert posts query without 'comments' column
insert_post_query = "INSERT INTO post (title, content, upvotes, media_file, date_of_creation, user_id) VALUES (?, ?, ?, ?, ?, ?)"
cursor.executemany(insert_post_query, post_data)


# Commit the changes to the database
conn.commit()

# Mockup comment data
comment_data = [
    ('This is a comment on post 1 by user 1', datetime.now(), 1, 1),
    ('This is a comment on post 1 by user 2', datetime.now(), 2, 1),
    # Add more comments as needed
]

# Insert comments
insert_comment_query = "INSERT INTO comment (content, date_of_creation, user_id, post_id) VALUES (?, ?, ?, ?)"
cursor.executemany(insert_comment_query, comment_data)

# Commit the changes to the database
conn.commit()

# Mockup friend data
# This assumes that user IDs 1, 2, and 3 have already been inserted into the user table
friend_data = [
    # User 1 is friends with User 2
    (1, 2),
    # User 1 is friends with User 3
    (1, 3),
    # User 2 is friends with User 3
    (2, 3),
    # Add more friend relationships as needed
]

# Insert friend relationships
insert_friend_query = "INSERT INTO friend (user_id, friend_id) VALUES (?, ?)"
cursor.executemany(insert_friend_query, friend_data)

# Commit the changes to the database
conn.commit()

print("Mockup data inserted successfully!")

# Close the database connection
conn.close()
