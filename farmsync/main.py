from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import re
import json
import os
import flask
from flask_babel import Babel, refresh
from farmsync.utility import app, logger, create_json_response, \
        create_dir, init_mysql_db
from farmsync import config
from farmsync import Image, comments
from farmsync.db import User

app.config.from_object(config.Config)

app.lang = 'en'
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

ERROR = "Error"
SUCCESS = "Success"

babel = Babel(app)

@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
        return session.get('lang', 'en')
    if session.get('lang'):
        return session.get('lang', 'en')
    return 'en'

@app.route('/change_lang',methods=['POST'])
def change_lang():
   session['lang'] = request.form['lang']
   return session['lang']

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        user_params = {
                        'username': username,
                        'password': password
                      }

	
        # Check if account exists using MySQL
        user = User(user_params)
        account = user.login().as_dict()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']

            if account['role'] == 'retailer':
                pr_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "products.json")
                with open(pr_path, "r") as f:
                    products = json.load(f)['products']
                return render_template('retailer.html', products=products)

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/products/<id>', methods=['GET'])
def get_Products(id):
    return render_template('products.html')


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('lang', None)
   # Redirect to login page
   return redirect(url_for('login'))


@app.route('/initdb', methods=['GET'])
def init_db():
    """
    Create MySql tables
    """
    return init_mysql_db()


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form.get('role', 'farmer')

        user_params = {
                        'username': username,
                        'password': password,
                        'email':email,
                        'role': role
                      }
        user = User(user_params)
        msg = user.register()

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        user = User()
        account = user.get_user_by_id(session['id'])
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/forum')
def forum():
    # Check if user is loggedin
    results = [{
      'id':1,
      'username':'Radhakrishna M',
      'description':'Dear France, I only can echo what is mentioned as a reason for this award! You are a great leader and also a great team member. Im proud to have you in Europe CS team. Orsi ',
      'dp':'Dp1.jpg',
      'time':'8:55 AM, Today',
      'images': [{'image_url':'capture.PNG'}, {'image_url':'target-spot.jpg'},{'image_url':'potato-blight.jpg'}, {'image_url':'large960.jpg'}],
      'comments': [{'username':'Radhakrishna M','time':'8:55 AM, Today', 'description':'Also a great team member. Im proud to have you in Europe CS team. Orsi ', 'dp':'Dp1.jpg'}, {'username':'Radhakrishna M', 'description':'You are a great leader and also a great team member. Im proud to have you in Europe CS team. Orsi ', 'dp':'Dp1.jpg','time':'8:55 AM, Today'}]
    },
    {
      'id':2,
      'username':'Milan Danga',
      'description':'Dear France, I only can echo what is mentioned as a reason for this award! You are a great leader and also a great team member. Im proud to have you in Europe CS team. Orsi ',
      'dp':'Dp1.jpg',
      'time':'8:55 AM, Today',
      'images': [{'image_url':'capture.PNG'}, {'image_url':'target-spot.jpg'},{'image_url':'potato-blight.jpg'}, {'image_url':'large960.jpg'}],
      'comments': [{'username':'Radhakrishna M', 'time':'8:55 AM, Today', 'description':'Also a great team member. Im proud to have you in Europe CS team. Orsi ', 'dp':'Dp1.jpg'}, {'username':'Radhakrishna M', 'description':'You are a great leader and also a great team member. Im proud to have you in Europe CS team. Orsi ', 'dp':'Dp1.jpg', 'time':'8:55 AM, Today'}]
    },]
    return render_template('forum.html', results = results)
    if 'loggedin' in session:
        # User is loggedin show them the home page
        #return render_template('forum.html', username=session['username'])
        pass
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/comments")
def get_comments():
    try:
        comments_cls = comments.Comments(limit=10)
        status, response_obj = comments_cls.get_comments()
        return jsonify({"results": response_obj}), 200
    except Exception as e:
        logger.error('Failed to upload images: {}'.format(str(e)))
        return create_json_response(ERROR, e)

@app.route("/addcomment", methods=['POST'])
def addcomment():
    try:
        activity_id = request.form['activity_id']
        commented_by = request.form['username']
        commented_header = request.form['subject']
        commented_desc = request.form['description']
        comments_cls = comments.Comments(limit=10)
        status, response_obj = comments_cls.add_comment(commented_by, activity_id, commented_header, commented_desc)
        if status is False:
            return create_json_response(ERROR, response_obj)
        return create_json_response(SUCCESS, response_obj)
    except Exception as e:
        logger.error('Failed to upload images: {}'.format(str(e)))
        return create_json_response(ERROR, e)
        
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    try:
        user = User()
        account = user.get_user_by_id(session['id']).as_dict()
        if request.method == 'GET':
            if 'loggedin' in session:
                return render_template('upload.html', account=account)
        username = account.get('username')
        user_uuid = account.get('user_uuid')
        user_role = account.get('user_role')
        form = request.form
        subject = form.get('subject')
        comment_desc = form.get('comment_desc')
        other_desc = form.get('other_desc')
        files = flask.request.files.getlist("file")
        if not files:
            raise Exception("No images found to process")

        img_params = {
                        'username': username,
                        'user_uuid': user_uuid,
                        'images': files,
                        'user_role': user_role,
                        'subject': subject,
                        'comment_desc': comment_desc,
                        'other_desc': other_desc
                    }
        img_cls = Image.Image(img_params)
        status, status_msg = img_cls.upload_image_to_s3()
        if status is False:
            return create_json_response(ERROR, status_msg)
        return redirect(url_for('forum'))
    except Exception as e:
        logger.error('Failed to upload images: {}'.format(str(e)))
        return create_json_response(ERROR, e)

@app.route("/dashboard")
def dashboard():
    try:
        form = request.form
        username = form.get('username')
        user_role = form.get('user_role')
        if not username:
            raise Exception("No username found to process")
        if not user_role:
            raise Exception("No user_role found to process")

        comments_cls = comments.Comments(10)
        status, response_msg = comments_cls.get_dashboard_results(user_name=username, user_role=user_role)
        if status is False:
            return create_json_response(ERROR, response_msg)
        return jsonify({"results": response_msg}), 200
    except Exception as e:
        logger.error('Failed to upload images: {}'.format(str(e)))
        return create_json_response(ERROR, e)

if __name__ == "__main__":
    from farmsync import s3_helper
    s3_helper.set_aws_credentials()
    app.run(host="0.0.0.0", port=5000, debug=True)

