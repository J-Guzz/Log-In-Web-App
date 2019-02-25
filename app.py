#Imports
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import sqlite3

app = Flask(__name__)

app.secret_key = "TEAM C"
db = "database.db"
tdb = "therapistDB.db"


#Ensures if the user is logged in.
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first!')
            return redirect(url_for('login'))
    return wrap
@app.route('/')
def send():
    return redirect(url_for('welcome'))

#Route page, gives the user options to log in or create account.
@app.route('/welcome')
def welcome():
    return render_template("welcome.html")

#Main menu for the patient.
@app.route('/main')
def main():
    return render_template("main.html")

#Main menu for therapist.
@app.route('/therapistMain')
def therapistMain():
    return render_template("therapistMain.html")

#Page for creating a patient and adding them to the database.
@app.route('/newPatient', methods=['GET', 'POST'])
def newPatient():
	if request.method == 'POST':
		username = request.form['username']
		name = request.form['name']
		password = request.form['password']
		gender = request.form['gender']
		email = request.form['email']
		para = (username,name,password,gender,email)
		connection = sqlite3.connect(db)
		connection.execute('INSERT INTO user VALUES(?,?,?,?,?)',para)
		connection.commit()
		session['logged_in'] = True #user is logged in when signed up
		flash('You are a new user!!!')
		return render_template('main.html')
	return render_template('newPatient.html')

#Page for creating a new therapist and adding them to the database.
@app.route('/newTherapist', methods=['GET', 'POST'])
def newTherapist():
	if request.method == 'POST':
		username = request.form['username']
		name = request.form['name']
		password = request.form['password']
		email = request.form['email']
		code = request.form['code']
		requiredCode = 'admincode'
		if code == requiredCode:
			para = (username,name,password,email)
			connection = sqlite3.connect(tdb)
			connection.execute('INSERT INTO therapist VALUES(?,?,?,?)',para)
			connection.commit()
			flash('New therpist has been created!!!')
	return render_template('newTherapist.html')

#Login page for therapists.
@app.route('/therapistLogin', methods=['GET', 'POST'])
def therapistLogin():
	error = None
	connection = sqlite3.connect(tdb)
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		c = connection.cursor()		# cursor needed to fetch from db
		c.execute('SELECT * from therapist WHERE username=(?) AND password=(?)',  (username, password))
		connection.commit() #ends connections elsewhere
		if c.fetchone() is not None:
			flash('You are logged in.')
			return render_template('therapistMain.html')
		else:
			error = 'Wrong username or password'
	return render_template('therapistLogin.html', error=error)

#Patient log in page.
#Flaks assumes method is a get request, if more is needed it must be declared.
#Post = post request.
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	posts = []
	connection = sqlite3.connect(db)
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		c = connection.cursor()		# cursor needed to fetch from db
		c.execute('SELECT * from user WHERE username=(?) AND password=(?)',  (username, password))
		connection.commit() #ends connections elsewhere
		if c.fetchone() is not None:
			session['logged_in'] = True
			flash('You are logged in.')
			posts = intervention(username)
			return render_template('main.html', posts=posts)
		else:
			error = 'Wrong username or password'
	return render_template('login.html', error=error)

#Page for assigning an intervention to a patient.
@app.route('/assignIntervention', methods=['GET', 'POST'])
def assignIntervention():
	if request.method == 'POST':
		username = request.form['username']
		intervention1 = request.form['intervention1']
		intervention2 = request.form['intervention2']
		intervention3 = request.form['intervention3']
		para = (intervention1,intervention2,intervention3,username)
		connection = sqlite3.connect(db)
		connection.execute('UPDATE user SET intervention1=(?),intervention2=(?),intervention3=(?) where username=(?)',para)
		connection.commit()
		flash('Intervention(s) has been assigned!')
	return render_template('aIntervention.html')

#Shows a list of patients from the database.
@app.route('/viewPatients')
def viewPatients():
	connection = sqlite3.connect(db)
	#connection.text_factory = bytes
	c = connection.cursor()
	c.execute('SELECT username, email from user')
	posts = [dict (username=row[0], email=row[1]) for row in c.fetchall()]
	connection.commit()
	return render_template('viewPatients.html', posts=posts)

#Search for a patient in the database.
@app.route('/searchPatient', methods=['GET', 'POST'])
def searchPatient():
	posts=[]
	if request.method == 'POST':
		username = request.form['username']
		posts = intervention(username)
	return render_template('searchPatient.html', posts=posts)

#Loggs the user out of the system and returns the to the /welcome page.
@app.route('/logout')
@login_required
def logout():
    #deletes key, by popping out legged in as True to None.
    session.pop('logged_in', None)
    flash('You were just logged out.')
    return redirect(url_for('welcome'))


def intervention(un):
	connection = sqlite3.connect(db)
	c = connection.cursor()
	c.execute('SELECT username, intervention1, intervention2, intervention3 from user WHERE username=(?) AND (intervention1=(?) or intervention2=(?) or intervention3=(?))',(un,'yes','yes','yes'))
	posts = [dict (username=row[0], intervention1=row[1], intervention2=row[2], intervention3=row[3]) for row in c.fetchall()]
	connection.commit()
	return posts



if __name__ == '__main__':
    app.run(debug = True)
