#Python Imports
from flask import Flask, render_template

#Routes Modules imports
from routes.users import users_mod
from routes.terminal import terminal_mod

#Creation of the app
app = Flask(__name__)

#Add routes modules
app.register_blueprint(users_mod,url_prefix='/users')
app.register_blueprint(terminal_mod,url_prefix='/terminal')

@app.route('/')
def login_page():
    return render_template('index.html',**locals())

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=4000,debug=True)