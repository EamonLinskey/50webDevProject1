import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


print("1")
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create Table for the First Time
def createReviews():
	db.execute("CREATE TABLE IF NOT EXISTS reviews (reviewer text, reviewer_id integer, review text, rating integer, book_id integer, id serial)")
	db.commit()
	return


createReviews()
print("2")

