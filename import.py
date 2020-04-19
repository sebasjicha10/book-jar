import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine=create_engine("postgres://rjnvzxxwghgcfb:367546554eeb44b550bdc1d735516aecd56f66b47fee0490a0a662b6a8cbdf77@ec2-52-202-146-43.compute-1.amazonaws.com:5432/d14a26rabqvt84")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book {title} by {author} published in {year}, isbn: {isbn}.")
    db.commit()

if __name__ == "__main__":
    main()