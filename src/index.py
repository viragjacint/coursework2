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

@app.route('/register')
def register():	
	return render_template('register.html')

@app.route('/cart')
def cart():	
	return render_template('cart.html')	

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
	if request.method == 'POST':
		if request.form['username'] != app.config['username']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['password']:
			error = 'Invalid password'
		else:
			session['user'] = True
			session['username'] = 'Jacint'
			return redirect(url_for('root'))
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