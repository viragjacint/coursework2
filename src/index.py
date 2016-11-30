from flask import *
from werkzeug import secure_filename
import sqlite3
import ConfigParser
import os
import socket
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)


def init(app):
	config = ConfigParser.ConfigParser()
	try:
		config_location = "etc/config.cfg"
		config.read(config_location)
		
		app.config['DEBUG'] = config.get("config", "debug")
		app.config['ip_address'] = config.get("config", "ip_address")
		app.config['port'] = config.get("config", "port")
		app.config['url'] = config.get("config", "url")
		app.config['username'] = config.get("config", "username")
		app.config['password'] = config.get("config", "password")
		app.config['db_location'] = 'db/shop.db'
		app.secret_key  = config.get("config", "secret_key")
		
		app.config['log_file'] = config.get("logging", "name")
		app.config['log_location'] = config.get("logging", "location")
		app.config['log_level'] = config.get("logging", "level")		
	except:
		print "Could not read configs from: ", config_location


		
def logs(app):
    log_pathname = app.config['log_location'] + app.config['log_file']
    file_handler = RotatingFileHandler(log_pathname, maxBytes=1024* 1024 * 10 , backupCount=1024)
    file_handler.setLevel( app.config['log_level'] )
    formatter = logging.Formatter("%(levelname)s | %(asctime)s |  %(module)s | %(funcName)s | %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.setLevel( app.config['log_level'] )
    app.logger.addHandler(file_handler)
		
@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404
	
@app.errorhandler(401)
def page_not_found(error):
	return render_template('401.html'), 404
	

@app.route('/')
def root():
	this_route = url_for('.root')
	app.logger.info("Logging a test message from "+this_route)
	sql = ('SELECT * FROM product_list WHERE featured = 1')
	connection = sqlite3.connect(app.config['db_location'])
	connection.row_factory = sqlite3.Row     		
	rows = connection.cursor().execute(sql).fetchall()	
	connection.close()
	return render_template('home.html', rows = rows)	

@app.route('/register', methods=['GET', 'POST'])
def register():	
	return render_template('register.html')
	
@app.route('/reg', methods=['GET', 'POST'])
def reg():
	if request.method == 'POST':
		email = request.form['email']
		first_name = request.form['firstname']
		last_name = request.form['surname']
		address = request.form['address1']
		address2 = request.form['address2']
		town = request.form['town']
		postcode = request.form['postcode']
		email = request.form['email']
		password = request.form['password']
		sql = ('SELECT * FROM customers WHERE email = ?')
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row 
		c = connection.cursor()
		c.execute(sql, [email])
		id_exists = c.fetchone()
		connection.close()
		if id_exists:
			error = 'The email address: ' + id_exists['email'] + " is already exist!"
			return render_template('register.html', error = error)
		else:
			sql2 = ('INSERT INTO customers (first_name, last_name, address, address2, town, postcode, email, password) VALUES (?,?,?,?,?,?,?,?)')			    		
			connection = sqlite3.connect(app.config['db_location'])
			connection.row_factory = sqlite3.Row 
			connection.cursor().execute(sql2, (first_name, last_name, address, address2, town, postcode, email, password))
			connection.commit()
			connection.close()
			success = "You have successfully registered. Please sign in!"
			return render_template('login.html', success = success)	
	else:
		print 'You are not allowed here'

	
@app.route('/cart')
def cart():	
	if session.get('user'):
		sql = ('SELECT * FROM cart WHERE customer_id = ?')
		id = session.get('id')
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		rows = connection.cursor().execute(sql, [id]).fetchall()
		connection.close()	
		return render_template('cart.html', rows = rows)
	else:
		sql = ('SELECT * FROM cart WHERE customer_id = ?')		
		id = socket.gethostbyname(socket.gethostname())
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		rows = connection.cursor().execute(sql, [id]).fetchall()
		connection.close()	
		return render_template('cart.html', rows = rows)

@app.route('/add', methods=['GET', 'POST'])
def add():	
	if session.get('user'):
		if request.method == 'POST':
			sql = ('INSERT INTO cart (customer_id,item,quantity, price, size, item_id, item_img, total) VALUES (?,?,?,?,?,?,?,?)')
			customer_id = session.get('id')
			get_id = request.form['id']
			total = int(request.form['price']) * int(request.form['quantity'])
			connection = sqlite3.connect(app.config['db_location'])
			connection.row_factory = sqlite3.Row     		
			connection.cursor().execute(sql, (customer_id,request.form['name'],request.form['quantity'],request.form['price'],request.form['size'],request.form['id'],request.form['img'], total ))
			connection.commit()
			connection.close()			
			return redirect(url_for('cart'))
	else:	
		sql = ('INSERT INTO cart (customer_id,item,quantity, price, size, item_id, item_img, total) VALUES (?,?,?,?,?,?,?,?)')
		customer_id = socket.gethostbyname(socket.gethostname())
		get_id = request.form['id']
		total = int(request.form['price']) * int(request.form['quantity'])
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		connection.cursor().execute(sql, (customer_id,request.form['name'],request.form['quantity'],request.form['price'],request.form['size'],request.form['id'],request.form['img'], total ))
		connection.commit()
		connection.close()			
		return redirect(url_for('cart'))

@app.route('/search', methods=['GET', 'POST'])
def search():	
	if request.method == 'POST':
		search = request.form['search']
		sql = 'SELECT * FROM product_list WHERE product_name LIKE "%'+search+'%" OR product_desc LIKE "%'+search+'%"'
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		rows = connection.cursor().execute(sql).fetchall()
		connection.close()
		return render_template('search.html', rows = rows)
	else:		
		return render_template('search.html')
		

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['username']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['password']:
			error = 'Invalid password'
		else:
			session['admin'] = True			
			return redirect(url_for('admin_prod'))
	return render_template('admin_login.html', error=error)	
	

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)    
    return redirect(url_for('admin'))
	
@app.route('/admin_prod', methods=['GET', 'POST'])
def admin_prod():
	if not session.get('admin'):
		abort(401)
	else:
		sql = ('SELECT * FROM product_list')
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		rows = connection.cursor().execute(sql).fetchall()
		connection.close()	
		return render_template('admin_prod.html', rows = rows)	
		
@app.route('/admin_cust', methods=['GET', 'POST'])
def admin_cust():
	if not session.get('admin'):
		abort(401)
	else:
		sql = ('SELECT * FROM customers')
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		rows = connection.cursor().execute(sql).fetchall()
		connection.close()	
		return render_template('admin_cust.html', rows = rows)		

@app.route('/delete_prod')
def delete_prod():
	if not session.get('admin'):
		abort(401)
	else:
		get_id = request.args.get('id')	
		sql = ('DELETE FROM product_list WHERE id = ?')		
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		connection.cursor().execute(sql, [get_id])
		connection.commit()
		connection.close()	
		return redirect(url_for('admin_prod'))
		
@app.route('/delete_cust')
def delete_cust():
	if not session.get('admin'):
		abort(401)
	else:
		get_id = request.args.get('id')	
		sql = ('DELETE FROM customers WHERE id = ?')		
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		connection.cursor().execute(sql, [get_id])
		connection.commit()
		connection.close()	
		return redirect(url_for('admin_cust'))
			
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
	if not session.get('admin'):
		abort(401)
	else:
		if request.method == 'POST':
			img = request.files['img']					
			img.save('static/img/product/'+img.filename)			
			sql = ('INSERT INTO product_list (product_name,product_desc,product_price,product_image) VALUES (?,?,?,?)')		
			connection = sqlite3.connect(app.config['db_location'])
			connection.row_factory = sqlite3.Row     		
			connection.cursor().execute(sql, (request.form['name'],request.form['description'],request.form['price'],img.filename))
			connection.commit()
			connection.close()	
			return redirect(url_for('admin_prod'))
			
@app.route('/admin_edit')
@app.route('/admin_edit/<id>')
def admin_edit(id):
	if not session.get('admin'):
		abort(401)
	else:				
		sql = ('SELECT * FROM product_list WHERE id = ?')
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		rows = connection.cursor().execute(sql, [id]).fetchall()					
		return render_template('admin_edit.html', rows = rows)
	
@app.route('/update', methods=['GET', 'POST'])
def update():
	if request.method == 'POST':	
		sql = ('UPDATE product_list SET product_name = ?, product_desc = ?, product_price = ? WHERE id = ?')		
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		connection.cursor().execute(sql, (request.form['name'],request.form['description'],request.form['price'],request.form['id']))
		connection.commit()			
		return redirect(url_for('admin_prod'))
			
@app.route('/admin_add')
def admin_add():
	if not session.get('admin'):
		abort(401)
	else:
		return render_template('admin_add.html')			
			
@app.route('/product')
def product():
	sql = ('SELECT * FROM product_list')
	connection = sqlite3.connect(app.config['db_location'])
	connection.row_factory = sqlite3.Row     		
	rows = connection.cursor().execute(sql).fetchall()
	connection.close()	
	return render_template('product.html', rows = rows)
	
@app.route('/details', methods=['GET'])
@app.route('/details/<id>', methods=['GET'])
def details(id):
	sql = ('SELECT * FROM product_list WHERE id = ?')
	connection = sqlite3.connect(app.config['db_location'])
	connection.row_factory = sqlite3.Row     		
	rows = connection.cursor().execute(sql, [id]).fetchall()
	connection.close()	
	return render_template('details.html', rows = rows)
	
@app.route('/login')
def login():	
	return render_template('login.html')	

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
	error = None
	if not session.get('user'):
		if request.method == 'POST':
			sql = ('SELECT * FROM customers WHERE email = ?')
			email = request.form['email']			
			connection = sqlite3.connect(app.config['db_location'])
			connection.row_factory = sqlite3.Row 
			c = connection.cursor()
			c.execute(sql, [email])
			customer = c.fetchone()
			connection.close()		
			if customer:			
				if request.form['password'] != customer['password']:
					error = 'Invalid password'
				else:
					session['user'] = True
					session['username'] = customer['first_name']
					session['id'] = customer['ID']
					return redirect(url_for('root'))
			else:
				error = "User doesn't exist. Please register"
				return render_template('register.html', error=error)
	else:
		error = session['username'] + " is already logged in. Please sign out first!"
	return render_template('login.html', error=error)

@app.route('/sign_out')
def sign_out():
    session.pop('user', None)    
    return redirect(url_for('root'))
	
@app.route('/delete', methods=['GET', 'POST'])
def delete():
	get_id = request.args.get('id')	
	sql = ('DELETE FROM cart WHERE id = ?')		
	connection = sqlite3.connect(app.config['db_location'])
	connection.row_factory = sqlite3.Row     		
	connection.cursor().execute(sql, [get_id])
	connection.commit()	
	return redirect(url_for('cart'))

if __name__ == '__main__':
	init(app)
	logs(app)
	app.run(
		host=app.config['ip_address'], 
		port=int(app.config['port']),
		threaded=True)