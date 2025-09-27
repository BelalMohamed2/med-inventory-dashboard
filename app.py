from flask import Flask, render_template, request, redirect
import pymysql
from routes import get_db_connection, init_routes
app = Flask(__name__)
init_routes(app)    
if __name__ == '__main__':
    app.run(debug=True)