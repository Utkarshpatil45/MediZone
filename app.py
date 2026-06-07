from flask import Flask, render_template, request, redirect, session, send_file
from flask_mysqldb import MySQL

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

from datetime import datetime
import os


app = Flask(__name__)
app.secret_key = "medizone_secret_123"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Patil'
app.config['MYSQL_DB'] = 'medizone'

mysql = MySQL(app)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
                    (name,email,password))
        mysql.connection.commit()
        cur.close()

        return "Registered Successfully!"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/products")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return f"Welcome {session['user_name']} to MediZone Dashboard"
    else:
        return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/products")
def products():
    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    return render_template("products.html", products=products)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    cur = mysql.connection.cursor()

    # check if product already in cart
    cur.execute("SELECT * FROM cart WHERE user_id=%s AND product_id=%s",
                (user_id, product_id))
    existing = cur.fetchone()

    if existing:
        cur.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND product_id=%s",
                    (user_id, product_id))
    else:
        cur.execute(
            "INSERT INTO cart(user_id, product_id, quantity) VALUES(%s,%s,1)",
            (user_id, product_id))

    mysql.connection.commit()
    cur.close()

    return redirect("/products")

# buy now route.
@app.route("/buy_now/<int:product_id>")
def buy_now(product_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    cur = mysql.connection.cursor()

    # get product
    cur.execute("SELECT name, price FROM products WHERE id=%s", (product_id,))
    product = cur.fetchone()

    # direct order insert
    total = product[1]

    cur.execute("""
        INSERT INTO orders(user_id, total_amount)
        VALUES(%s,%s)
    """, (user_id, total))

    mysql.connection.commit()
    cur.close()

    return f"Order placed for {product[0]} ✔"


# cart view route.
@app.route("/cart")
def view_cart():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT products.id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id=%s
    """, (user_id,))

    items = cur.fetchall()

    total = 0
    for item in items:
        total += item[2] * item[3]

    cur.close()

    return render_template("cart.html", items=items, total=total)


@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cur = mysql.connection.cursor()

    # check quantity
    cur.execute("SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s",
                (user_id, product_id))
    item = cur.fetchone()

    if item:
        if item[0] > 1:
            # quantity 1 se zyada hai → decrease
            cur.execute("UPDATE cart SET quantity = quantity - 1 WHERE user_id=%s AND product_id=%s",
                        (user_id, product_id))
        else:
            # quantity 1 hai → pura delete
            cur.execute("DELETE FROM cart WHERE user_id=%s AND product_id=%s",
                        (user_id, product_id))

    mysql.connection.commit()
    cur.close()

    return redirect("/cart")

# Quantity Increase Route
@app.route("/increase/<int:product_id>")
def increase(product_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE cart
        SET quantity = quantity + 1
        WHERE user_id=%s AND product_id=%s
    """, (user_id, product_id))

    mysql.connection.commit()
    cur.close()

    return redirect("/cart")

# Quantity Decrease Route
@app.route("/decrease/<int:product_id>")
def decrease(product_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT quantity FROM cart
        WHERE user_id=%s AND product_id=%s
    """, (user_id, product_id))

    item = cur.fetchone()

    if item:
        if item[0] > 1:
            cur.execute("""
                UPDATE cart
                SET quantity = quantity - 1
                WHERE user_id=%s AND product_id=%s
            """, (user_id, product_id))
        else:
            cur.execute("""
                DELETE FROM cart
                WHERE user_id=%s AND product_id=%s
            """, (user_id, product_id))

    mysql.connection.commit()
    cur.close()

    return redirect("/cart")

# checkout route
@app.route("/checkout")
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cur = mysql.connection.cursor()

    # Get cart items
    cur.execute("""
        SELECT products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id=%s
    """, (user_id,))

    items = cur.fetchall()

    if not items:
        return "Cart is empty"

    total = 0
    for item in items:
        total += item[1] * item[2]

    # Insert into orders
    cur.execute("INSERT INTO orders(user_id, total_amount) VALUES(%s,%s)",
                (user_id, total))
    mysql.connection.commit()

    order_id = cur.lastrowid

    # Insert order items
    for item in items:
        cur.execute("""
            INSERT INTO order_items(order_id, product_name, price, quantity)
            VALUES(%s,%s,%s,%s)
        """, (order_id, item[0], item[1], item[2]))

    mysql.connection.commit()

    # Clear cart
    cur.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))
    mysql.connection.commit()
    cur.close()

    # Generate PDF
    file_path = f"invoice_{order_id}.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>MediZone Medical Store</b>", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Invoice ID: {order_id}", styles['Normal']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    table_data = [["Product", "Price", "Qty", "Subtotal"]]

    for item in items:
        subtotal = item[1] * item[2]
        table_data.append([item[0], item[1], item[2], subtotal])

    table_data.append(["", "", "Total", total])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    return send_file(file_path, as_attachment=True)


# orders view route.
@app.route("/orders")
def orders():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id, total_amount, order_date, status
        FROM orders
        WHERE user_id=%s
        ORDER BY order_date DESC
    """, (user_id,))

    orders = cur.fetchall()
    cur.close()

    return render_template("orders.html", orders=orders)


@app.route("/book_appointment", methods=["POST"])
def book_appointment():

    name = request.form["name"]
    email = request.form["email"]
    age = int(request.form["age"])
    appointment_date = request.form["date"]
    time = request.form["time"]
    doctor = request.form["doctor"]

    cur = mysql.connection.cursor()

    cur.execute("""
    INSERT INTO appointments(name, email, doctor, age, appointment_date, time, status)
    VALUES(%s,%s,%s,%s,%s,%s,'Pending')
""", (name, email, doctor, age, appointment_date, time))

    mysql.connection.commit()
    cur.close()

    return render_template("successappointment.html")
    # return redirect("/success")

# doctor_consultation route.
@app.route("/doctor_consult")
def doctor_consult():
    return render_template("doctor_consult.html")


# my appointments route.
@app.route("/my_appointments")
def my_appointments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM appointments")
    data = cur.fetchall()
    cur.close()
    return render_template("my_appointments.html", appointments=data)


if __name__ == "__main__":
    app.run(debug=True)