from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error

DB_NAME = "Dictionary.db"
app = Flask(__name__)
app.secret_key = "12345678"


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

    query = "SELECT Category, id FROM Category"

    cur = con.cursor()
    cur.execute(query)
    Category_list = cur.fetchall()
    con.close()

    email = session.get("email")
    query4 = "SELECT fname, lname, teacher FROM customer WHERE email=?"
    con4 = create_connection(DB_NAME)
    cur4 = con4.cursor()
    cur4.execute(query4, (email,))
    User_list = cur4.fetchall()
    con4.close()
    return render_template('home.html', Categorys=Category_list, Users=User_list, teacher=is_teacher(),
                           logged_in=is_logged_in())


@app.route('/word/<category>/<id>')
def render_wordpage(category, id):
    con = create_connection(DB_NAME)

    query = "SELECT Maori, English, Category, Definition, Level, Image, id FROM Dictionary where Category=?"

    cur = con.cursor()
    cur.execute(query, (category,))
    Dictionary_list = cur.fetchall()
    con.close()

    con2 = create_connection(DB_NAME)

    query2 = "SELECT Category, id FROM Category where id=?"

    cur2 = con2.cursor()
    cur2.execute(query2, (id,))
    id_list = cur2.fetchall()
    con2.close()

    con = create_connection(DB_NAME)

    query = "SELECT Category, id FROM Category"

    cur = con.cursor()
    cur.execute(query)
    Category_list = cur.fetchall()
    con.close()

    email = session.get("email")
    query4 = "SELECT fname, lname, teacher FROM customer WHERE email=?"
    con4 = create_connection(DB_NAME)
    cur4 = con4.cursor()
    cur4.execute(query4, (email,))
    User_list = cur4.fetchall()
    con4.close()

    Update_word_list = []

    for word in Dictionary_list:
        update_word = [item for item in word]
        if update_word[5] is None:
            update_word[5] = "noimage"
        Update_word_list.append(update_word)

    return render_template('word.html', Dictionarys=Dictionary_list, ids=id_list, Users=User_list, teacher=is_teacher(),
                           Categorys=Category_list, Update_words=Update_word_list, logged_in=is_logged_in(), )


@app.route('/detail/<maori>/<id>', methods=["GET", "POST"])
def render_detailpage(maori, id):
    con = create_connection(DB_NAME)

    query = "SELECT Maori, English, Category, Definition, Level, Image FROM Dictionary where Maori=?"

    cur = con.cursor()
    cur.execute(query, (maori,))
    Dictionary_list = cur.fetchall()
    con.close()

    con2 = create_connection(DB_NAME)

    query2 = "SELECT Category FROM Category"

    cur2 = con2.cursor()
    cur2.execute(query2)
    Category_list = cur2.fetchall()
    con2.close()

    email = session.get("email")
    query4 = "SELECT fname, lname, teacher FROM customer WHERE email=?"
    con4 = create_connection(DB_NAME)
    cur4 = con4.cursor()
    cur4.execute(query4, (email,))
    User_list = cur4.fetchall()
    con4.close()

    Update_word_list = []

    for word in Dictionary_list:
        update_word = [item for item in word]
        if update_word[5] is None:
            update_word[5] = "noimage"
        Update_word_list.append(update_word)

    if request.method == "POST":
        Maori = request.form.get('Maori')
        English = request.form.get('English')
        Category = request.form.get('Category')
        Definition = request.form.get("Definition")
        Level = request.form.get("Level")

        con3 = create_connection(DB_NAME)

        query3 = "Update Dictionary SET Maori=?, English=?, Category=?, Definition=?, Level=?, Image=Null WHERE id=?"

        cur3 = con3.cursor()

        Category_list = ["Actions", "Animals", "Clothing", "Culture / Religion", "Descriptive", "Emotions", "Food",
                         "Math / Number", "Outdoors", "People", "Places", "Plants", "School", "Sport", "Technology",
                         "Time", "Others"]
        re_Category = False
        if Category not in Category_list:
            re_Category = True
        print(Maori, English, Category, Definition, Level, id)
        if re_Category is True:
            return redirect("/edit?error=Category+is+invalid")
        else:
            cur3.execute(query3, (Maori, English, Category, Definition, Level, id))

        con3.commit()
        con3.close()
        return redirect("/")

    return render_template('detail.html', Dictionarys=Dictionary_list, Categorys=Category_list, Users=User_list,
                           teacher=is_teacher(), Update_words=Update_word_list, logged_in=is_logged_in())


@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        query = """SELECT id, email, password, teacher FROM customer where email=?"""
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()

        try:
            userid = user_data[0][0]
            db_password = user_data[0][2]
            teacherid = user_data[0][3]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        if db_password != password:
            print(db_password, password)
            return redirect("/login?error=Email+invalid+or+password+incorrect")


        session["email"] = email
        session["userid"] = userid
        session["teacher"] = teacherid
        print(session)
        return redirect("/")
    return render_template('login.html', teacher=is_teacher(), logged_in=is_logged_in())


@app.route('/signup', methods=["GET", "POST"])
def render_signup_page():
    if request.method == "POST":
        print(request.form)
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get("password")
        password2 = request.form.get("password2")
        teacher = request.form.get("teacher")

        if password != password2:
            return redirect("/signup?error=Passwords+dont+match")

        con = create_connection(DB_NAME)

        query = "INSERT INTO customer(id, fname, lname, email, password, teacher) VALUES(NULL,?,?,?,?,? or NULL)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, password, teacher))
        except sqlite3.IntegrityError:
            return redirect("/signup?error=Email+is+already+used")

        con.commit()
        con.close()
        return redirect("/")

    return render_template('signup.html', teacher=is_teacher(), logged_in=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect(request.referrer + '?message=See+you+next+time!')


@app.route('/delete/<maori>')
def delete(maori):
    query = "DELETE FROM Dictionary where Maori=?"
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (maori,))

    print("word deleted")

    con.commit()
    con.close()
    return redirect("/")


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


def is_teacher():
    if session.get("teacher") is None:
        print("not teacher")
        return False
    else:
        print("teacher")
        return True


@app.route('/edit', methods=["GET", "POST"])
def render_edit_page():
    if request.method == "POST":
        print(request.form)
        Maori = request.form.get('Maori')
        English = request.form.get('English')
        Category = request.form.get('Category')
        Definition = request.form.get("Definition")
        Level = request.form.get("Level")

        con = create_connection(DB_NAME)

        query = "INSERT INTO Dictionary(Maori, English, Category, Definition, Level, Image) VALUES(?,?,?,?,?,Null)"

        cur = con.cursor()

        Category_list = ["Actions", "Animals", "Clothing", "Culture / Religion", "Descriptive", "Emotions", "Food",
                         "Math / Number", "Outdoors", "People", "Places", "Plants", "School", "Sport", "Technology",
                         "Time", "Others"]
        re_Category = False
        if Category not in Category_list:
            re_Category = True

        if re_Category is True:
            return redirect("/edit?error=Category+is+invalid")
        else:
            cur.execute(query, (Maori, English, Category, Definition, Level))

        con.commit()
        con.close()

    con2 = create_connection(DB_NAME)

    query2 = "SELECT Category FROM Category"

    cur2 = con2.cursor()
    cur2.execute(query2)
    Category_list = cur2.fetchall()
    con2.close()

    email = session.get("email")
    query4 = "SELECT fname, lname, teacher FROM customer WHERE email=?"
    con4 = create_connection(DB_NAME)
    cur4 = con4.cursor()
    cur4.execute(query4, (email,))
    User_list = cur4.fetchall()
    con4.close()

    return render_template('edit.html', Categorys=Category_list, Users=User_list, teacher=is_teacher(),
                           logged_in=is_logged_in())


app.run(host='0.0.0.0', debug=True)
