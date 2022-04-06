from flask import Flask, render_template
import sqlite3
from sqlite3 import Error

DB_NAME = "Dictionary.db"

app = Flask(__name__)

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None

@app.route('/')
def render_homepage():
    con = create_connection(DB_NAME)

    query = "SELECT Maori, English, Category, Definition, Level FROM Dictionary"

    cur = con.cursor()
    cur.execute(query)
    Dictionary_list = cur.fetchall()
    con.close()

    return render_template('home.html', Dictionarys=Dictionary_list)


@app.route('/word/<category>')
def render_wordpage(category):
    con = create_connection(DB_NAME)

    query = "SELECT Maori, English, Category, Definition, Level FROM Dictionary where Category=?"

    cur = con.cursor()
    cur.execute(query, (category, ))
    Dictionary_list = cur.fetchall()
    con.close()
    return render_template('word.html', Dictionarys=Dictionary_list)

@app.route('/detail/<maori>')
def render_detailpage(maori):
    con = create_connection(DB_NAME)

    query = "SELECT Maori, English, Category, Definition, Level FROM Dictionary where Maori=?"

    cur = con.cursor()
    cur.execute(query, (maori,))
    Dictionary_list = cur.fetchall()
    con.close()
    return render_template('detail.html', Dictionarys=Dictionary_list)

app.run(host='0.0.0.0', debug=True)
