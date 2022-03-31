from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def render_homepage():
    return render_template('home.html')

app.run(host='0.0.0.0', debug=True)
