from flask import Flask, request, render_template, redirect, url_for, session
import random
import mysql.connector as sql
import hashlib
from dotenv import load_dotenv
from flask_session import Session
import send

load_dotenv()

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "admin1234"
Session(app)
sqlc = sql.connect(
    host="localhost", user="<USER>", password="<PASSWORD>", database="pessato"
)
cur = sqlc.cursor(buffered=True)


@app.route("/resetadmin")
def resetadmin():
    session["admin"] = False
    session["cafe_admin"] = False
    return "done"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        srn = request.form.get("srn")
        cur.execute(f'SELECT phone,email FROM log1 WHERE SRN="{srn}";')
        x = cur.fetchone()
        ph, email = x[0], x[1]
        session["email"] = x[1]
        if ph and email:
            session["srn"] = srn
            gotp = genotp()
            session["gotp"] = gotp[1]
            subject = "OTP for PESSATO"
            body = f"Your OTP is {gotp[0]}"
            send._email(email, subject, body)
            send._msg(ph, gotp[0])
            session["logged_in"] = False
            return redirect(url_for("home"))
    return render_template("index.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    srn = session.get("srn")
    gotp = session.get("gotp")
    if srn:
        cur.execute(f'SELECT count(orderno) FROM adminmanageorders WHERE srn="{srn}";')
        if cur.fetchall()[0][0] > 4:
            return redirect(url_for("uorders"))
    if gotp is None or srn is None:
        return redirect(url_for("index"))
    if "cart" in request.form:
        session["srn"] = srn
        return redirect(url_for("cart"))
    if request.method == "POST" or session["logged_in"]:
        if "otp" in request.form or session["logged_in"]:
            entered_otp = request.form.get("otp")
            if "backfromcart" in request.form:
                entered_otp = gotp
            cur.execute(f'SELECT wallet FROM log1 WHERE SRN="{srn}";')
            wallet = round(cur.fetchone()[0], 2)
            session["wallet"] = wallet
            if validate_otp(entered_otp, gotp) or session["logged_in"]:
                session["logged_in"] = True
                cur.execute("SELECT Food,Price FROM menu;")
                data = []
                x = cur.fetchall()
                for i in x:
                    di1 = {}
                    di1["food"] = i[0]
                    di1["price"] = i[1]
                    data.append(di1)
                cur.execute(f"SELECT * FROM orders WHERE srn='{srn}';")
                x = cur.fetchall()
                orders = []
                for i in x:
                    di1 = {}
                    di1["orderno"] = i[0]
                    di1["order"] = i[1]
                    di1["transactionid"] = i[3][-6::]
                    di1["status"] = i[4]
                    di1["quantity"] = i[5]
                    orders.append(di1)
                cur.execute(f"SELECT * from carts WHERE srn='{srn}';")
                x = cur.fetchall()
                cart = []
                for i in x:
                    di1 = {}
                    di1["food"] = i[0]
                    di1["price"] = i[1]
                    di1["quantity"] = i[2]
                    cart.append(di1)
                cur.execute(f"DELETE FROM carts WHERE srn='{srn}';")
                sqlc.commit()
                return render_template(
                    "home.html",
                    data=data,
                    orders=orders,
                    wallet=wallet,
                    cart=cart,
                    srn=srn,
                    success=True,
                )
    return render_template("home.html", success=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        cod = request.form.get("pcode")
        srn = request.form.get("srn")
        phone = request.form.get("phone")
        mail = request.form.get("email")
        phno = cod + phone
        if srn and phone:
            cur.execute(f"INSERT INTO log1 VALUES('{srn}','{phno}',0,'{mail}');")
            sqlc.commit()
            return redirect(url_for("index"))
    return render_template(
        "register.html", data=[{"code": "+91"}]
    )


@app.route("/cartAdd", methods=["POST"])
def cartAdd():
    quant = request.get_json()
    if quant[2] > 1:
        cur.execute(
            f'UPDATE carts SET quantity={quant[2]} WHERE srn="{quant[3]}" AND food="{quant[0]}";'
        )
    else:
        cur.execute(f"INSERT INTO carts VALUES{tuple(quant)};")
    sqlc.commit()
    return redirect(url_for("cart"))


@app.route("/cartSub", methods=["POST"])
def cartSub():
    quant = request.get_json()
    if quant[2] > 0:
        cur.execute(
            f'UPDATE carts SET quantity={quant[2]} WHERE srn="{quant[3]}" AND food="{quant[0]}";'
        )
    elif quant[2] == 0:
        cur.execute(f'DELETE FROM carts WHERE srn="{quant[3]}" AND food="{quant[0]}";')
    sqlc.commit()
    return redirect(url_for("cart"))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    srn = session.get("srn")
    if srn:
        cur.execute(f'SELECT * FROM carts WHERE srn="{srn}";')
        cart = []
        x = cur.fetchall()
        for i in x:
            di1 = {}
            di1["food"] = i[0]
            di1["price"] = i[1]
            di1["quantity"] = i[2]
            cart.append(di1)
        return render_template("cart.html", cart=cart, srn=srn)
    else:
        return redirect(url_for("index"))


@app.route("/receipt", methods=["POST"])
def receipt():
    srn = session.get("srn")
    wallbal = session.get("wallet")
    cur.execute(f'SELECT price,quantity FROM carts WHERE srn="{srn}";')
    x = cur.fetchall()
    grandtotal = sum(i[0] * i[1] for i in x)
    grandtotal = round(1.18 * grandtotal, 2)

    if wallbal >= grandtotal:
        pdfli = []
        cur.execute(f'SELECT * FROM carts WHERE srn="{srn}";')
        cart = cur.fetchall()
        cur.execute("SELECT orderno FROM orders")
        try:
            currorder = cur.fetchall()[-1][0] + 1
        except:
            currorder = 1
        tID = createTransID(srn, grandtotal, currorder)
        pdfli.append(currorder)
        for i in cart:
            cur.execute(
                f'INSERT INTO orders VALUES({currorder},"{i[0]}",{i[1]},"{tID}","paid",{i[2]},"{srn}");'
            )
            pdfli.append([i[0], i[2], i[1]])
        wallbal -= grandtotal
        cur.execute(f'UPDATE log1 SET wallet={wallbal} WHERE srn="{srn}";')
        orderotp = genotp(3)
        cur.execute(
            f'INSERT INTO adminmanageorders VALUES({currorder},"{orderotp[0]}","{srn}","paid");'
        )
        sqlc.commit()
        send.getter(pdfli)
        send._createPDF()
        email = session.get("email")
        subject = "Order receipt by PESSATO"
        body = f"Find your order receipt attached to this mail for order:{currorder}."
        send._email(email, subject, body, True)
        return redirect(url_for("uorders"))
    else:
        return redirect(url_for("addmoni"))


@app.route("/uorders", methods=["GET", "POST"])
def uorders():
    wallet = session.get("wallet")
    srn = session.get("srn")
    cur.execute(f'SELECT * FROM adminmanageorders WHERE srn="{srn}";')
    userorders = cur.fetchall()
    passOrders = []
    orderindex = []
    passOrderItems = []
    for i in userorders:
        data = {}
        data["orderno"] = i[0]
        cur.execute(f'SELECT * FROM orders WHERE srn="{srn}" AND orderno={i[0]};')
        orderItems = cur.fetchall()
        for j in orderItems:
            datao = {}
            datao["orderno"] = j[0]
            datao["food"] = j[1]
            datao["price"] = j[2]
            datao["status"] = j[4]
            passOrderItems.append(datao)
        orderindex.append(i[0])
        data["otp"] = i[1]
        passOrders.append(data)
    if request.method == "POST" and "orderotp" in request.form:
        selectOrder = request.form.get("orderno")
        oi = orderindex.index(int(selectOrder))
        otpSelected = request.form.get("orderotp")
        diForOtp = passOrders[oi]
        checkotp = diForOtp["otp"]
        if validate_otp(otpSelected, checkotp):
            cur.execute(f"DELETE FROM adminmanageorders WHERE orderno={selectOrder};")
            cur.execute(
                f'UPDATE orders SET status="collected" WHERE srn="{srn}" AND orderno={selectOrder};'
            )
            sqlc.commit()
            return redirect(url_for("uorders"))
        return redirect(url_for("uorders"))
    return render_template(
        "uorders.html",
        wallet=wallet,
        passOrders=passOrders,
        passOrderItems=passOrderItems,
    )


@app.route("/addmoni", methods=["GET", "POST"])
def addmoni():
    srn = session.get("srn")
    if request.method == "POST":
        amt = float(request.form.get("amt"))
        cur.execute(f'SELECT * FROM monireq WHERE srn="{srn}";')
        if cur.fetchall():
            cur.execute(f'UPDATE monireq SET amt={amt} WHERE srn="{srn}";')
        else:
            cur.execute(f'INSERT INTO monireq VALUES("{srn}",{amt});')
        sqlc.commit()
    return render_template("addmoni.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST" and "amt" in request.form:
        srn = request.form.get("srn")
        amt = request.form.get("amt")
        if request.form["submit_req"] == "add":
            cur.execute(f'UPDATE log1 SET wallet=wallet+{amt} WHERE srn="{srn}";')
        cur.execute(f'DELETE FROM monireq WHERE srn="{srn}";')
        sqlc.commit()
        return redirect(url_for("admin"))
    if request.method == "POST" and "login" in request.form or session["admin"]:
        session["admin"] = True
        uname = request.form.get("uname")
        upass = request.form.get("password")
        if upass:
            check = hashpass(upass)
        if (
            session["admin"]
            or check
            == "ac9689e2272427085e35b9d3e3e8bed88cb3434828b43b86fc0596cad4c6e270"
            and uname == "admin"
        ):
            cur.execute("SELECT * FROM monireq;")
            x = cur.fetchall()
            reqlist = []
            for i in x:
                data = {}
                data["srn"] = i[0]
                data["amt"] = i[1]
                reqlist.append(data)
            return render_template("admin.html", success=True, reqlist=reqlist)
    return render_template("admin.html")


@app.route("/cafeOrders", methods=["GET", "POST"])
def cafeOrders():
    if request.method == "POST" and "login" in request.form or session["cafe_admin"]:
        session["cafe_admin"] = True
        uname = request.form.get("uname")
        upass = request.form.get("password")
        if upass:
            check = hashpass(upass)
        if (
            session["admin"]
            or check
            == "ac9689e2272427085e35b9d3e3e8bed88cb3434828b43b86fc0596cad4c6e270"
            and uname == "admin"
        ):
            cur.execute(
                'SELECT srn FROM adminmanageorders WHERE status="paid" GROUP BY srn;'
            )
            srns = []
            x = cur.fetchall()
            for i in x:
                srns.append(i[0])
            cur.execute("SELECT * FROM orders;")
            x = cur.fetchall()
            allOrders = []
            for i in x:
                data = {}
                data["orderno"] = i[0]
                data["food"] = i[1]
                data["status"] = i[4]
                data["quantity"] = i[5]
                data["srn"] = i[6]
                allOrders.append(data)
            return render_template(
                "cafeOrders.html", srns=srns, allOrders=allOrders, success=True
            )
    return render_template("cafeOrders.html")


@app.route("/changeStatus", methods=["GET", "POST"])
def changeStatus():
    if request.method == "POST":
        orderno = request.form.get("orderno")
        food = request.form.get("food")
        if request.form["submit_status"] == "ready":
            cur.execute(
                f'UPDATE orders SET status="ready to collect" WHERE orderno={orderno} AND food="{food}";'
            )
        elif request.form["submit_status"] == "collected":
            cur.execute(
                f'UPDATE orders SET status="collected" WHERE orderno={orderno} AND food="{food}";'
            )
            cur.execute(
                f'UPDATE adminmanageorders SET status="collected" WHERE orderno={orderno};'
            )
        sqlc.commit()
    return redirect(url_for("cafeOrders"))


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


def genotp(type=3):
    gotp = random.randint(100000, 999999)
    sha256 = hashlib.sha256()
    sha256.update(str(gotp).encode())
    string_hash = sha256.hexdigest()
    print(f"Your OTP is : {gotp}")
    if type == 1:
        return string_hash
    elif type == 2:
        return gotp
    elif type == 3:
        return [gotp, string_hash]
    else:
        return string_hash


def hashpass(hasher):
    sha256 = hashlib.sha256()
    sha256.update(hasher.encode())
    string_hash = sha256.hexdigest()
    return string_hash


def validate_otp(eotp, genotp):
    sha256 = hashlib.sha256()
    sha256.update(str(eotp).encode())
    ehotp = sha256.hexdigest()
    return ehotp == genotp or eotp == genotp


def createTransID(srn, moni, order):
    s = str(srn) + str(moni) + str(order)
    sha256 = hashlib.sha256()
    sha256.update(s.encode())
    transID = sha256.hexdigest()
    return transID


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", debug=True)
