from flask import Blueprint, render_template, url_for, redirect, request, flash, send_from_directory, jsonify, current_app
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from . import db, socketio
from .models import User, Comment, Post, Friend, Message
import os
from flask import current_app 
from .models import Tag
from datetime import datetime
from flask_socketio import emit, join_room, leave_room




auth = Blueprint('auth',__name__)
bcrypt = Bcrypt()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            print(f'{user.password} and {password} and {check_password_hash(user.password, password)}')
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('auth.page'))
            else:
                flash('Incorrect password, try again.', category='error')        

        else:
            print('Email does not exist.')

    return render_template("home.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/page')
def page():
    return render_template('page.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        print(f'user from db {user}')
        if user:
            flash('Email already exists.')
        elif password != password2:
            flash('Passwords do not match please try again!')
            print('Passwords do not match.')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            new_user = User(username=username,email=email, password=hashed_password, pfp='cattest.jpg',about_me='', description='')
            db.session.add(new_user)
            db.session.commit()

            print(f'User {new_user} created')
            return redirect(url_for('views.home'))

    return render_template("register.html")

@auth.route('/user-edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        try:
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    print(filepath)
                    current_user.pfp = filename  
        except Exception as e:
            print(f"Error: {e}")
            flash(f"An error occurred: {e}", category='error')
        

        about = request.form.get('about')
        if about is not None:
            current_user.about_me = about

        description = request.form.get('description')
        if description is not None:
            current_user.description = description

        if 'tags' in request.form:
            submitted_tags = request.form.getlist('tags')
            current_user.tags = []

            for tag_name in submitted_tags:
                tag = Tag.query.filter_by(tag_name=tag_name).first()
                if not tag:
                    tag = Tag(tag_name=tag_name)
                    db.session.add(tag)
                current_user.tags.append(tag)

        db.session.commit()
        db.session.refresh(current_user)
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('auth.page'))

    user_tags = [tag.tag_name for tag in current_user.tags]
    return render_template('edit.html', user=current_user, user_tags=user_tags)


@auth.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@auth.route('/posts', methods=['POST', 'GET'])
@login_required
def posts():
    posts = Post.query.order_by(Post.date_of_creation.desc()).all()
    return render_template('posts.html', posts=posts)

@auth.route('/create-post', methods=['GET', 'POST'])
@login_required 
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        media_file = request.files['media_file']
        date_of_creation = datetime.now()

        if media_file and media_file.filename != '':
            filename = secure_filename(media_file.filename)
            media_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            media_file.save(media_path)

            new_post = Post(title=title, content=content, media_file=filename, user_id=current_user.id, date_of_creation=date_of_creation)

        else:
            new_post = Post(title=title, content=content, user_id=current_user.id, date_of_creation=date_of_creation)

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('auth.posts')) 
    
    return render_template('create_post.html')  

@auth.route('/delete-post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)

    db.session.delete(post_to_delete)
    db.session.commit()
    flash('Post deleted successfully.', category='success')

    return redirect(url_for('auth.posts'))



def add_comment_to_post(post_id):
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, post_id=post_id, 
                            user_id=current_user.id,
                            date_of_creation=datetime.utcnow())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added.', 'success')
    else:
        flash('Comment cannot be empty.', 'error')
    return redirect(url_for('views.posts', post_id=post_id))

@auth.route('/upvote/<int:post_id>', methods=['POST'])
@login_required
def upvote(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user in post.upvoted_by:
        post.upvoted_by.remove(current_user)
        upvoted = False
    else:
        post.upvoted_by.append(current_user)
        upvoted = True
    
    db.session.commit()
    return jsonify({'upvoted': upvoted, 'upvotes': post.upvoted_by.count()}) 
@auth.route('/users')
@login_required
def users():
    all_users = User.query.filter(User.id != current_user.id).all()
    return render_template('users.html', users=all_users)

@auth.route('/user-profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    recipient = user

    are_friends = Friend.query.filter(
        ((Friend.user_id == current_user.id) & (Friend.friend_id == user.id)) |
        ((Friend.user_id == user.id) & (Friend.friend_id == current_user.id))
    ).first() is not None

    return render_template('user.html', user=user, are_friends=are_friends, recipient=recipient)

@auth.route('/add-friend/<int:user_id>', methods=['GET', 'POST'])
@login_required
def add_friend(user_id):
    friend = User.query.get_or_404(user_id)

    existing_friendship = Friend.query.filter_by(
        user_id=current_user.id, friend_id=friend.id
    ).first()

    if existing_friendship:
        flash("You are already friends.", category='error')
    else:
        new_friendship = Friend(user_id=current_user.id, friend_id=friend.id)
        db.session.add(new_friendship)
        db.session.commit()
        flash("Friend request sent!", category='success')

    return redirect(url_for('auth.user_profile', user_id=user_id))

@auth.route('/unfriend/<int:friend_id>', methods=['POST'])
@login_required
def unfriend(friend_id):
    friendship = Friend.query.filter_by(
        user_id=current_user.id, 
        friend_id=friend_id
    ).first()

    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash('You have unfriended the user.', category='success')
    else:
        flash('Friendship not found.', category='error')

    return redirect(url_for('auth.user_profile', user_id=friend_id))

@auth.route('/search-users', methods=['GET'])
@login_required
def search_users():
    all_tags = Tag.query.all()
    username_query = request.args.get('username')
    tag_filter = request.args.getlist('tags')

    query = User.query.filter(User.id != current_user.id)
    if username_query:
        query = query.filter(User.username.ilike(f'%{username_query}%'))

    if tag_filter:
        query = query.join(User.tags).filter(Tag.id.in_(tag_filter))

    filtered_users = query.all()
    return render_template('users.html', users=filtered_users, all_tags=all_tags)

@auth.route('/friends')
@login_required
def friends():
    friend_relations = Friend.query.filter(
        (Friend.user_id == current_user.id) | (Friend.friend_id == current_user.id)
    ).all()

    friend_ids = set()
    for relation in friend_relations:
        friend_ids.add(relation.user_id if relation.user_id != current_user.id else relation.friend_id)

    friends = User.query.filter(User.id.in_(friend_ids)).all()

    return render_template('friends.html', friends=friends)


@auth.route('/view_post/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@auth.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment_content = request.form.get('comment_content')
    date_of_creation = datetime.now()


    if comment_content:
        comment = Comment(content=comment_content, post_id=post.id, user_id=current_user.id,date_of_creation=date_of_creation)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added', category='success')
    else:
        flash('Comment cannot be empty', category='error')

    return redirect(url_for('auth.view_post', post_id=post_id))


@auth.route('/chat/<int:recipient_id>')
@login_required
def chat(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) |
        ((Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.date_of_creation.asc())
    return render_template('chat.html', recipient=recipient, messages=messages)


@socketio.on('send_message')
def handle_send_message_event(data):
    recipient_id = data['recipient_id']
    msg = data['msg']
    date_of_creation = datetime.now()
    user = User.query.get(current_user.id)


    message = Message(sender_id=current_user.id, recipient_id=recipient_id, body=msg, date_of_creation=date_of_creation)
    db.session.add(message)
    db.session.commit()
    
    room_ids = [str(current_user.id), str(recipient_id)]
    room_ids.sort()  
    room = "-".join(room_ids)

    emit('new_message', {'msg': msg, 'sender_id': current_user.id, 'username': user.username}, room=room)



@socketio.on('join_chat')
def on_join(data):
    user_id = current_user.id
    recipient_id = data['recipient_id']
    room_ids = [str(current_user.id), str(recipient_id)]
    room_ids.sort()  
    room = "-".join(room_ids)    
    join_room(room)


@socketio.on('leave_room')
def on_leave(data):
    room = data['room']
    leave_room(room)

@auth.route('/chat-selection')
@login_required
def chat_selection():
    # Logic to list available recipients
    return render_template('chat_selection.html', recipients=recipients)
