from flask import Flask, render_template, request, redirect
import pymysql
def get_db_connection():
        return pymysql.connect(
            host="localhost",
            user = "root",
            password = "2560065belal",
            database = "media_stock"
        )

app = Flask(__name__)

@app.route('/')
def home():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    # Example query to fetch total items
    mycursor.execute("SELECT count(*) FROM items where quantity>0 and expiry_date > CURDATE()")
    total_items = mycursor.fetchone()[0]
    # Example query to fetch total categories
    mycursor.execute("SELECT COUNT(DISTINCT category) FROM items")
    total_categories = mycursor.fetchone()[0]
    #Exmple query to fetch expired items
    mycursor.execute("SELECT COUNT(*) FROM items WHERE expiry_date < CURDATE() and quantity>0")
    expired_items = mycursor.fetchone()[0]
    #Example query to fetch out of stock items
    mycursor.execute("SELECT COUNT(*) FROM items WHERE quantity= 0")
    out_of_stock = mycursor.fetchone()[0]
    mycursor.close()
    mydb.close()
    return render_template('dashboard.html', total_items=total_items, total_categories=total_categories, expired_items=expired_items, out_of_stock=out_of_stock)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method  == 'POST':
        name = request.form['name'].capitalize()
        quantity = request.form['quantity']
        category = request.form['category']
        expiry_date = request.form['expiry_date']
        mydb = get_db_connection()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT name, quantity, category, expiry_date, id FROM items where quantity>0 and expiry_date > CURDATE() ORDER BY category ASC , name ASC")
        items = mycursor.fetchone()
        if name == items[0] :
            new_quantity = items[1] + int(quantity)
            sql = "UPDATE items SET quantity = %s WHERE name = %s"
            val = (new_quantity, name)
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
            mydb.close()
            return redirect('/view')
        sql = "INSERT INTO items (name, quantity, category, expiry_date) VALUES (%s, %s, %s, %s)"
        val = (name, quantity, category, expiry_date)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        mydb.close()
        return redirect('/view')
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    return render_template('add.html')

@app.route('/view')
def view_items():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name, quantity, category, expiry_date, id FROM items where quantity>0 and expiry_date > CURDATE() ORDER BY category ASC , name ASC")
    items = mycursor.fetchall()
    mycursor.close()
    return render_template('viewitem.html', items=items)

@app.route('/outofstock')
def out_of_stock():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name, quantity, category, expiry_date FROM items where quantity=0")
    items = mycursor.fetchall()
    mycursor.close()
    return render_template('outofstock.html', items=items)

@app.route('/expireditems')
def expired_items():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name, quantity, category, expiry_date FROM items where expiry_date < CURDATE() and quantity>0")
    items = mycursor.fetchall()
    
    mycursor.close()
    return render_template('expireditems.html', items=items)

@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def itemdetails(item_id):
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name, quantity, category, expiry_date , id FROM items where expiry_date > CURDATE() and quantity>0 and id=%s", (item_id,))
    items = mycursor.fetchone()
    if request.method == 'POST':
        action = request.form['action']
        if action == 'add':
            quantity = int (request.form['quantity'])
            sql = "UPDATE items SET quantity = quantity + %s WHERE id = %s"
            val = (quantity, item_id)
            mycursor.execute(sql, val)
        elif action == 'remove':
            quantity = int (request.form['quantity'])
            sql = "UPDATE items SET quantity = quantity - %s WHERE id = %s"
            val = (quantity, item_id)
            mycursor.execute(sql, val)
        elif action == 'delete':
            sql = "DELETE FROM items WHERE id = %s"
            val = (item_id)
            mycursor.execute(sql, val)
        mydb.commit()
        return redirect('/view')

    mycursor.close()
    return render_template('itemdetalis.html', items=items)



if __name__ == '__main__':
    app.run(debug=True)
    