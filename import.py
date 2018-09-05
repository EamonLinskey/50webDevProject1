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
# db.execute("CREATE TABLE IF NOT EXISTS books (isbn text, title text, author text, year integer, id serial)")
# db.commit()

# Populate table 

def populate():
	with open('books.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				#print(f'Column names are {", ".join(row)}')
				line_count += 1
			else:
				db.execute ("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": row[0], "title": row[1], "author": row[2], "year": row[3]})
				#print(f'{row[1]} with isbn number {row[0]} was written by {row[2]} in {row[3]}.')
				line_count += 1
		db.commit()
		print(f'Processed {line_count} lines.')

populate()


