import os
import hashlib 
import random 
import string
import requests

from flask import Flask, session, render_template, request, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def getReviewsGoodReads(isbn):
	
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "FLNGqmKMgOHY8Zh0tLuQ", "isbns": isbn})
	
	print(res.json()['books'][0]['work_reviews_count'])
	print(res.json()['books'][0]['average_rating'])
	
	return (res.json()['books'][0]['work_reviews_count'], res.json()['books'][0]['average_rating'])
	

#hashing and salting passwords to keep them secure from https://kasperfred.com/posts/how-to-store-user-passwords-securely
def hash_password(password, salt=None, iterations=100000):
	# Do type checking
	if not type(password) == type("String"):
		raise TypeError("Password should be a string")

	# if no salt is given
	# generate 16 alphanumeric long salt using system random
	if not salt:
		salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

	# encode to make it compatible with hashlib algorithm
	encoded_password = bytes(password, encoding='utf-8')
	encoded_salt = bytes(salt, encoding='utf-8')

	pass_hash = hashlib.sha3_512(encoded_password+encoded_salt).hexdigest()

	# use iterative hashing
	for _ in range(iterations):
		pass_hash = hashlib.sha3_512(bytes(pass_hash, encoding="utf-8")+encoded_password).hexdigest()

	return (pass_hash, salt)

#def generate_salt():
#	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

#def create_users():
#	db.execute()
#	db.commit()

def register_new_user(username, password):
	#Creates table the first time
	#db.execute("CREATE TABLE IF NOT EXISTS users (username text, hashedPass text, salt text, id serial)")
	#db.commit()

	hashedPass, salt = hash_password(password)
	#print(hashedPass, salt)
	#username= "Eamo"
	#test = "sdfsf"
	#hashedPass= "Hashedbrowns"
	#salt= "salty"
	#userId = 10

	user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
	if(user == None):
		db.execute ("INSERT INTO users (username, hashedPass, salt) VALUES (:username, :hashedPass, :salt)",
			{"username": username, "hashedPass": hashedPass, "salt": salt})
		db.commit()
	else:
		print("This username is already in use")
	print("done")

	#db.execute("INSERT INTO Users (username, hashedPass, salt) VALUES (u, h, s)")
	#print("executed")
	#db.commit()
	#print("commited")
	#return ("exectued")

def validate_password(password, pw_hash_tuple):
	# Do input validation
	if not len(pw_hash_tuple) == 2:
		raise ValueError("pw_hash_tuple should have length 2")

	if not type(password) == type('string'):
		raise TypeError("password should be a string")

	for item in pw_hash_tuple:
		if not type(item) == type("string"):
			raise TypeError("items in pw_hash_tuple should be strings")


	stored_pw_hash = pw_hash_tuple[0]
	stored_pw_salt = pw_hash_tuple[1]

	# compute the hash of guesspassword using the same salt
	user_pw_hash_tuple = hash_password(password, salt=stored_pw_salt)

	# compare the two hashes
	if user_pw_hash_tuple[0] == stored_pw_hash:
		return True
	else:
		return False

def authenticate_user(username, password):
	if(db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone() == None):
		print("this user does not exist")
		return (False, None)
	else:
		(user, hashedPass, salt, userId) = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
		#print(validate_password(password, (hashedPass, salt)))
		return (validate_password(password, (hashedPass, salt)), userId)

register_new_user("NewerEamon", "SECETPASSWORD")
print(authenticate_user("NewerEamon", "SECETPASSWORD"))
#pw_hash_tuple = ("e844001b57c811f64129f35e40072d1decdbee5188c6d3e576cd85586b6ca50307c2df5c0d976c5b446af59d6434009aed2f29e730b1e73713d1c63c03fd9ea0", "N1AUJ5HTRW7KAIEL")
#guess_password = "SECETPAsSSWORD"
#print (validate_password(guess_password, pw_hash_tuple)) # True



@app.route("/")
def index():
	session["view"] = "index"
	return render_template("index.html")

@app.route("/registration")
def registration():
	try:
		if session["userId"]:
			session["view"] = "index"
			return render_template("index.html")
		else:
			session["view"] = "registration"
			return render_template("registration.html")
	except:
		return render_template("registration.html")

@app.route("/registred", methods=["POST"])
def registred():
	password = request.form.get("password")
	username = request.form.get("username")
	existingUser = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
	if existingUser != None:
		flash('That username is already in use')
		session["view"] = "registration"
		return render_template("registration.html")
	else:
		print(password)
		register_new_user(username, password)
		session["userId"] = authenticate_user(username, password)[1]
		session["username"] = username
		session["view"] = "registred"
		return render_template("registred.html")

@app.route("/login")
def login():
	try:
		if session["userId"]:
			session["view"] = "index"
			return render_template("index.html")
		else:
			session["view"] = "login"
			return render_template("login.html")
	except:
		session["view"] = "login"
		return render_template("login.html")
    
@app.route("/loggedIn", methods=["POST"])
def loggedIn():
	password = request.form.get("password")
	username = request.form.get("username")

	if authenticate_user(username, password)[0]:
		session["userId"] = authenticate_user(username, password)[1]
		session["username"] = username
		session["view"] = "search"
		return render_template("search.html", id=session["userId"])
	else:
		flash('Incorrect Username or Password')
		session["view"] = "login"
		return render_template("login.html")

@app.route("/logOut")
def logOut():
	session["userId"] = None
	session["username"] = None
	session["view"] = "index"
	return render_template("index.html")

@app.route("/search")
def search():
	try:
		if session["userId"]:
			search = request.args.get('search')
			results = db.execute("SELECT * FROM books WHERE title ~* :search OR isbn ~* :search OR author ~* :search", {"search": search}).fetchall()
			session["view"] = "search"
			return render_template("search.html", results=results)
		else:
			session["view"] = "login"
			return render_template("login.html")
	except:
		session["view"] = "login"
		return render_template("login.html")

@app.route("/book/<bookId>")
def book(bookId):
	try:
		if session["userId"]:
			book = db.execute("SELECT * FROM books WHERE id = :bookId", {"bookId": bookId}).fetchone()
			reviews = db.execute("SELECT * FROM reviews WHERE book_id = :bookId", {"bookId": bookId}).fetchall()
			reviewed = db.execute("SELECT * FROM reviews WHERE reviewer_id = :reviewerId and book_id = :bookId", {"reviewerId": session["userId"], "bookId": bookId}).fetchone()
			goodReads = getReviewsGoodReads(book[0])
			session["view"] = "book"
			return render_template("book.html", book=book, reviews=reviews, reviewed=reviewed, goodReads=goodReads)
		else:
			session["view"] = "login"
			return render_template("login.html")
	except:
		session["view"] = "login"
		return render_template("login.html")

@app.route("/review/<bookId>", methods=["POST"])
def review(bookId):
	try:
		if session["userId"]:
			reviewed = db.execute("SELECT * FROM reviews WHERE reviewer_id = :reviewerId and book_id = :bookId", {"reviewerId": session["userId"], "bookId": bookId}).fetchone()
			print(session["userId"])
			print(bookId)
			print(reviewed)
			review = request.form.get("review")
			rating = request.form.get("rating")
			book = db.execute("SELECT * FROM books WHERE id = :bookId", {"bookId": bookId}).fetchone()
			goodReads = getReviewsGoodReads(book[0])
			reviews = db.execute("SELECT * FROM reviews WHERE book_id = :bookId", {"bookId": bookId}).fetchall()

			if reviewed == None:
				db.execute ("INSERT INTO reviews (reviewer, reviewer_id, review, rating, book_id) VALUES (:reviewer, :reviewer_id, :review, :rating, :bookId)",
					{"reviewer": session["username"], "reviewer_id": session["userId"], "review": review, "rating": rating, "bookId": bookId})
				db.commit()
				reviews = db.execute("SELECT * FROM reviews WHERE book_id = :bookId", {"bookId": bookId}).fetchall()
				reviewed = db.execute("SELECT * FROM reviews WHERE reviewer_id = :reviewerId and book_id = :bookId", {"reviewerId": session["userId"], "bookId": bookId}).fetchone()
			session["view"] = "book"
			return render_template("book.html", book=book, reviews=reviews, reviewed=reviewed, goodReads=goodReads)
		else:
			session["view"] = "login"
			return render_template("login.html")
	except:
		session["view"] = "login"
		return render_template("login.html")

@app.route("/api/<isbn>")
def api(isbn):
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "FLNGqmKMgOHY8Zh0tLuQ", "isbns": isbn})
	goodReads = getReviewsGoodReads(isbn)
	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

	return jsonify(title= book[1], author= book[2], year= book[3], isbn= isbn, review_count= goodReads[0], average_score= goodReads[1])
	



