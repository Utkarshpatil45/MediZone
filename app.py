# from flask import Flask, render_template, request, redirect, url_for
# import mysql.connector


# app = Flask(__name__)

# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="Patil",
#     database="MediZone"
# )

# cursor = db.cursor()

# # 🏠 Home route
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         name = request.form["name"]
#         email = request.form["email"]
#         password = request.form["password"]

#         # check if user already exists
#         cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
#         existing_user = cursor.fetchone()

#         if existing_user:
#             return "User already exists!"

#         # insert new user
#         sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
#         values = (name, email, password)

#         cursor.execute(sql, values)
#         db.commit()

#         return "Registration Successful!"

#     return render_template("register.html")


# # 🔐 LOGIN ROUTE 👇 (YAHAN PASTE KARNA HAI)
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         sql = "SELECT * FROM users WHERE email=%s AND password=%s"
#         values = (email, password)

#         cursor.execute(sql, values)
#         user = cursor.fetchone()

#         if user:
#             return "Login Successful!"
#         else:
#             return "Invalid Credentials"

#     return render_template("login.html")

# # product_table

# from flask import request

# @app.route("/products")
# def products():

#     search = request.args.get("search")

#     if search:
#         cursor.execute(
#             "SELECT * FROM products WHERE name LIKE %s",
#             ('%' + search + '%',)
#         )
#     else:
#         cursor.execute("SELECT * FROM products")

#     all_products = cursor.fetchall()

#     return render_template(
#         "products.html",
#         products=all_products,
#         search=search
#     )
# # 🛒 ADD TO CART ROUTE (FIXED)
# @app.route("/add_to_cart/<int:product_id>")
# def add_to_cart(product_id):

#     user_id = 1

#     cursor.execute(
#         "SELECT * FROM cart WHERE user_id=%s AND product_id=%s",
#         (user_id, product_id)
#     )
#     item = cursor.fetchone()

#     if item:
#         cursor.execute(
#             "UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND product_id=%s",
#             (user_id, product_id)
#         )
#     else:
#         cursor.execute(
#             "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
#             (user_id, product_id, 1)
#         )

#     db.commit()

#     return redirect(url_for("cart"))

# # Increase Quantity
# @app.route("/increase/<int:product_id>")
# def increase(product_id):

#     user_id = 1

#     cursor.execute("""
#         UPDATE cart 
#         SET quantity = quantity + 1 
#         WHERE user_id=%s AND product_id=%s
#     """, (user_id, product_id))

#     db.commit()

#     return redirect(url_for("cart"))


# # decrease Quantity
# @app.route("/decrease/<int:product_id>")
# def decrease(product_id):

#     user_id = 1

#     cursor.execute("""
#         SELECT quantity FROM cart 
#         WHERE user_id=%s AND product_id=%s
#     """, (user_id, product_id))

#     item = cursor.fetchone()

#     if item and item[0] > 1:
#         cursor.execute("""
#             UPDATE cart 
#             SET quantity = quantity - 1 
#             WHERE user_id=%s AND product_id=%s
#         """, (user_id, product_id))
#     else:
#         cursor.execute("""
#             DELETE FROM cart 
#             WHERE user_id=%s AND product_id=%s
#         """, (user_id, product_id))

#     db.commit()

#     return redirect(url_for("cart"))

# # remove product
# @app.route("/remove/<int:product_id>")
# def remove(product_id):

#     user_id = 1

#     cursor.execute("""
#         DELETE FROM cart 
#         WHERE user_id=%s AND product_id=%s
#     """, (user_id, product_id))

#     db.commit()

#     return redirect(url_for("cart"))



# # cart route
# @app.route("/cart")
# def cart():

#     user_id = 1

#     cursor.execute("""
#         SELECT products.id,
#                products.name,
#                products.price,
#                cart.quantity
#         FROM cart
#         JOIN products ON cart.product_id = products.id
#         WHERE cart.user_id = %s
#     """, (user_id,))

#     rows = cursor.fetchall()

#     items = []
#     total = 0

#     for r in rows:
#         product_id = r[0]
#         name = r[1]
#         price = float(r[2] or 0)
#         qty = int(r[3] or 0)

#         subtotal = price * qty
#         total += subtotal

#         items.append((product_id, name, price, qty, subtotal))

#     return render_template("cart.html", items=items, total=total)


# # checkout
# @app.route("/checkout")
# def checkout():
#     return render_template("checkout.html", total=100)

# # Appointment
# @app.route("/Appointment", methods=["GET", "POST"])
# def appointment():

#     if request.method == "POST":

#         name = request.form["name"]
#         email = request.form["email"]
#         doctor = request.form["doctor"]
#         date = request.form["date"]
#         time = request.form["time"]

#         cursor.execute("""
#             INSERT INTO appointments (name, email, doctor, date, time)
#             VALUES (%s, %s, %s, %s, %s)
#         """, (name, email, doctor, date, time))

#         db.commit()

#         return "Appointment Booked Successfully!"

#     return render_template("appointment.html")



# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "MediZone is Live 🚀"

if __name__ == "_main_":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))