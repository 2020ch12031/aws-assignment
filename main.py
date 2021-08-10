from flask import Flask,render_template,request,redirect,session,url_for
from flask_mysqldb import MySQL
import MySQLdb

app=Flask(__name__)
app.secret_key = "1234567890"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "test"
app.config["MYSQL_DB"] = "login"

db = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if 'username' in request.form and 'password' in request.form:
			email = request.form['username']
			password = request.form['password']
			cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM login.login_data WHERE email=%s AND password=%s",(email, password))
			info = cursor.fetchone()
			if info is not None:
				if info['email'] == email and info['password'] == password:
					session['loginsuccess'] = True
					session['email'] = info['email']
					session['user_id'] = info['user_id']
					session['name'] = info['name']
					return redirect(url_for('profile'))
			else:
				return redirect(url_for('index'))
	return render_template("login.html")

@app.route('/new', methods=['GET', 'POST'])
def new_user():
	if request.method == "POST":
		if "one" in request.form and "two" in request.form and "three" in request.form:
			name = request.form['one']
			email = request.form['two']
			password = request.form['three']
			cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
			cur.execute("INSERT INTO login.login_data(name, email, password)VALUES(%s,%s,%s)",(name, email, password))
			db.connection.commit()
			return redirect(url_for('index'))
	return render_template("register.html")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
	if request.method == "POST" and session['loginsuccess'] == True:
		if "one" in request.form and "two" in request.form and "three" in request.form:
			desc = request.form['one']
			amount = request.form['two']
			transactionDate = request.form['three']
			cursor_exp = db.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor_exp.execute("INSERT INTO login.expense(email, user_id, expenseDesc, expenseDate, expenseAmount)VALUES(%s,%s,%s,%s,%s)",
			                    (session['email'], session['user_id'],desc, transactionDate, amount))
			db.connection.commit()
	if session['loginsuccess'] == True:
		sql_arg = (session['user_id'],)
		user_name = session['name'] 
		user_email = session['email']
		headings = ("Expense Description", "Amount", "Date")
#		curs = db.connection.cursor(MySQLdb.cursors.DictCursor)
		curs = db.connection.cursor()
		curs.execute("SELECT E.expenseDesc As Description, E.expenseAmount AS Amount, E.expenseDate AS Date FROM login.login_data AS L, login.expense AS E WHERE L.user_id=E.user_id AND L.user_id=%s ORDER BY E.expenseDate", sql_arg)
		account = curs.fetchall()
		if account is not None:
			return render_template("display.html", user_name=user_name, user_email=user_email, headings=headings, account=account)
		else:
#			new_curs = db.connection.cursor(MySQLdb.cursors.DictCursor)
			new_curs = db.connection.cursor()
			new_curs.execute("SELECT L.name AS Name, L.email AS Email FROM login.login_data AS L WHERE L.user_id=%s", sql_arg)
			account = new_curs.fetchone()
			if new_account is not None:
				return render_template("profile.html", user_name=user_name, user_email=user_email, account=account)

	return redirect(url_for('index'))

@app.route('/display', methods=['GET', 'POST'])
def display():
	if request.method == "POST" and session['loginsuccess'] == True:
		if "one" in request.form and "two" in request.form and "three" in request.form:
			desc = request.form['one']
			amount = request.form['two']
			transactionDate = request.form['three']
			cursor_exp = db.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor_exp.execute("INSERT INTO login.expense(email, expenseDesc, expenseDate, expenseAmount)VALUES(%s,%s,%s,%s)",(session['email'], desc, transactionDate, amount))
			db.connection.commit()
	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	session.pop('loginsuccess', None)
	return redirect(url_for('index'))

@app.route('/monthly_avg')
def monthly_avg():
	if session['loginsuccess'] == True:
		sql_arg = ("'%M'", "'%Y'", session['user_id'],)
		user_name = session['name'] 
		user_email = session['email']
		headings = ("Amount", "Date", "Year")
		curs = db.connection.cursor()
		curs.execute("SELECT Avg(E.expenseAmount) AS AverageExpense, DATE_FORMAT(E.expenseDate, %s) AS Month, DATE_FORMAT(E.expenseDate, %s) AS Year FROM login.expense AS E WHERE E.user_id=%s GROUP BY Month, Year ORDER BY Month, Year;", sql_arg)
		account = curs.fetchall()
		return render_template("monthly_avg.html", user_name=user_name, user_email=user_email, headings=headings, account=account)
	return redirect(url_for('profile'))

if __name__ == '__main__':
	app.run(debug=True)
