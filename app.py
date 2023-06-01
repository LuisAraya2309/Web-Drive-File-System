#Python Imports
from flask import Flask, render_template
from db.db_connection import file_system_db

#Creation of the app
app = Flask(__name__)

@app.route('/')
def login_page():
    return render_template('index.html',**locals())

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=4000,debug=True)