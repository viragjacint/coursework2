from flask import *
from werkzeug import secure_filename
import sqlite3
import ConfigParser
import os
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
		sql = ('SELECT * FROM cart WHERE customer_id = 0')		
		connection = sqlite3.connect(app.config['db_location'])
		connection.row_factory = sqlite3.Row     		
		rows = connection.cursor().execute(sql).fetchall()
		connection.close()	
		return render_template('cart.html', rows = rows)
		

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
	
if __name__ == '__main__':
	init(app)
	logs(app)
	app.run(
		host=app.config['ip_address'], 
		port=int(app.config['port']),
		threaded=True)