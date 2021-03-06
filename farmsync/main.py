from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import re
import json
import os
import requests
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


def get_comodity_records():
    api_endpoint = "http://ec2-18-191-11-104.us-east-2.compute.amazonaws.com:3000/api/Commodity"
    data = requests.get(api_endpoint).json()
    if not data:
        return []
    
    result = []
    ignore_products = ["SEED1", "SEED2"]
    default_records = [
                        {
                            "product_id": "P23A15x-PA46",
                            "owner_name": "Farmer",
                            "retailer_name": "Agriteam Services",
                            "crop_type": "Soybean",
                            "helium_color": "Black",
                            "storage_temp": "12",
                            "storage_batch_id": "B-47856",
                            "treatment_batch_id": "B-47857",
                            "treatment_type": "ILEVO",
                            "unit": "100",
                            "packing_type": "Bag",
                            "final_product_id": "P23A15x-SU28"
                        },
                        {
                            "product_id": "001A48X",
                            "owner_name": "Farmer",
                            "retailer_name": "Alliance Agri-Turf Bolton",
                            "crop_type": "Soybean",
                            "helium_color": "Dark Brown",
                            "storage_temp": "20",
                            "storage_batch_id": "B-47893",
                            "treatment_batch_id": "B-47894",
                            "treatment_type": "Inoculent Nodulator Pro",
                            "unit": "25",
                            "packing_type": "Pro box",
                            "final_product_id": "001A48X-S001"
                        }
                    ]
    for item1 in data:
        if item1['tradingSymbol'] not in ignore_products:
            item = {}
            item['product_id'] = item1['tradingSymbol']
            item['owner_name'] = item1['owner'].split("#")[1]
            item['retailer_name'] = "Advantage Co-op Redvers"
            item['crop_type'] = "Soybean"
            item["helium_color"] = "Dark Brown"
            item["storage_temp"] = "23"
            item["storage_batch_id"] = "B-48967"
            item["treatment_batch_id"] = "B-48968"
            item["treatment_type"] = "Fungicide Trilex 2000"
            item["unit"] = "50"
            item["packing_type"] = "Jumbo"
            item["final_product_id"] = "P005a27X-SU34"
            result.append(item)
    result.extend(default_records)
    return result
    
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

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


def get_trade_records(product_id):
    api_endpoint = "http://ec2-18-191-11-104.us-east-2.compute.amazonaws.com:3000/api/Trade"
    data = requests.get(api_endpoint).json()
    if not data:
        return []
    
    result = []
    for item in data:
        if product_id in item['commodity']:
            item['product_id'] = product_id
            item['owner_name'] = item['newOwner'].split("#")[1]
            item['product_name'] = "corn seeds" # default product name for now
            item['retailer_name'] = "Agro Plus Inc." # default retailer_name
            result.append(item)
    return result


@app.route('/products/<id>', methods=['GET'])
def get_Products(id):
    transactions = get_trade_records(id)
    print(transactions)
    #return render_template('products.html')
    return render_template('transactions.html', transactions=transactions)


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
        products = get_comodity_records()
        static_products = [
                        {
                            "Product_ID": "P3546",
                            "Product_Name": "Corn",
                            "Inventory_ID": "IN2342",
                            "Unit_price": "2300",
                            "Stock_Quantity": "50",
                            "Stock_type": "Bag",
                            "Inventory_Value": "115000",
                            "Batch_ID": "22322",
                            "Shipment_order_date": "23-04-2021",
                            "Shipment_Received_date": "27-04-2021",
                        },
                        {
                            "Product_ID": "P3396",
                            "Product_Name": "Corn",
                            "Inventory_ID": "IN8987",
                            "Unit_price": "1890",
                            "Stock_Quantity": "75",
                            "Stock_type": "Probox",
                            "Inventory_Value": "141750",
                            "Batch_ID": "23423",
                            "Shipment_order_date": "24-04-2021",
                            "Shipment_Received_date": "28-04-2021",
                        },
                        {
                            "Product_ID": "P3401",
                            "Product_Name": "Corn",
                            "Inventory_ID": "IN7766",
                            "Unit_price": "2500",
                            "Stock_Quantity": "100",
                            "Stock_type": "Jumbo",
                            "Inventory_Value": "250000",
                            "Batch_ID": "21232",
                            "Shipment_order_date": "25-04-2021",
                            "Shipment_Received_date": "27-04-2021",
                        },
                        {
                            "Product_ID": "27P31",
                            "Product_Name": "Rice",
                            "Inventory_ID": "IN6799",
                            "Unit_price": "1200",
                            "Stock_Quantity": "50",
                            "Stock_type": "Bag",
                            "Inventory_Value": "60000",
                            "Batch_ID": "33453",
                            "Shipment_order_date": "25-04-2021",
                            "Shipment_Received_date": "27-04-2021",
                        },
                        {
                            "Product_ID": "25P35",
                            "Product_Name": "Rice",
                            "Inventory_ID": "IN8787",
                            "Unit_price": "1200",
                            "Stock_Quantity": "100",
                            "Stock_type": "Jumbo",
                            "Inventory_Value": "120000",
                            "Batch_ID": "33453",
                            "Shipment_order_date": "23-04-2021",
                            "Shipment_Received_date": "28-04-2021",
                        },
                        {
                            "Product_ID": "P2334A",
                            "Product_Name": "Soybean",
                            "Inventory_ID": "IN1232",
                            "Unit_price": "1100",
                            "Stock_Quantity": "100",
                            "Stock_type": "Bag",
                            "Inventory_Value": "110000",
                            "Batch_ID": "48967",
                            "Shipment_order_date": "23-04-2021",
                            "Shipment_Received_date": "28-04-2021",
                        },
                        {
                            "Product_ID": "P005a27X",
                            "Product_Name": "Soybean",
                            "Inventory_ID": "IN2342",
                            "Unit_price": "1800",
                            "Stock_Quantity": "25",
                            "Stock_type": "Jumbo",
                            "Inventory_Value": "45000",
                            "Batch_ID": "48967",
                            "Shipment_order_date": "26-04-2021",
                            "Shipment_Received_date": "28-04-2021",
                        },
                        {
                            "Product_ID": "P0025A",
                            "Product_Name": "Soybean",
                            "Inventory_ID": "IN1432",
                            "Unit_price": "1750",
                            "Stock_Quantity": "50",
                            "Stock_type": "Probox",
                            "Inventory_Value": "87500",
                            "Batch_ID": "47856",
                            "Shipment_order_date": "26-04-2021",
                            "Shipment_Received_date": "28-04-2021",
                        }

                        
                    ]
        print("products", json.dumps(products, indent=2))
        return render_template('home.html', products=products, static_products=static_products, username=session['username'])
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

