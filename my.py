import os, requests
from supabase import create_client, Client
from dotenv import load_dotenv
from flask import *

load_dotenv()
TG_TOKEN = os.environ["TG_TOKEN"]
TG_USER_ID = os.environ["user"] 



def send_telegram_message(
    name: str,
    contact: str,
    comment: str,
    user_id: str | int = TG_USER_ID,
    token: str = TG_TOKEN,
    timeout: int = 10,
) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    text = (
        "📩 <b>New client</b>\n\n"
        f"<b>Name:</b> {name}\n"
        f"<b>Contact:</b> {contact}\n"
        f"<b>Comment:</b>\n{comment}"
    )

    response = requests.post(
        url,
        json={
            "chat_id": user_id,
            "text": text,
            "parse_mode": "HTML",
        },
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(data)

    return data


supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data
def add_product(product_name, seller_id, image_url, price):
    response = supabase.table("products").insert({
        "product_name": product_name,
        "seller_id": seller_id,
        "image_url": image_url,
        "price": price
    }).execute()
    return response.data
def selectProducts(seller_id):
    response = (
        supabase.table("products")
        .select("*")
        .eq("seller_id", seller_id)
        .execute()
    )
    return response.data


def delete_product(product_id):
    response = supabase.table("products").delete().eq("id", product_id).execute()
    return response.data

def add_info (name, text):
    response = (
        supabase.table("users")
        .insert({"korystuWATCH": name, "password": text})
        .execute()
)
def dump (id):
    response = (
        supabase.table("users")
        .delete()
        .eq("id", id)
        .execute()
    )

def update(id, name, password):
    response = (
        supabase.table("users")
        .update({"korystuWATCH": name, "password": password})
        .eq("id", id)
        .execute()
)

def gI():
    response = supabase.table('users').select("*").execute()
    users = response.data
    return users
app = Flask(__name__)
app.secret_key="shosrandomne"
def verificate(user, password):
    response = (
        supabase.table("users")
        .select("id, korystuWATCH, password")
        .eq("korystuWATCH", user)
        .execute()
    )
    print(response)
    if response.data:
        row = response.data[0]
        if row["korystuWATCH"] == user and row["password"] == password:
            return row["id"]
        return None
    return None
#verificate("tertre", "676767")


@app.route("/order_product/<int:id>", methods=["GET", "POST"])
def order_product(id):
    if session.get("user_id") is None:
        return redirect("/")
    response = (
        supabase.table("products")
        .select("*")
        .eq("id", id)
        .execute()
    )
    product = response.data

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        address = request.form["address"]
        quantity = request.form["quantity"]

        product_name = product[0]["product_name"] if product else f"id {id}"

        comment = (
            f"Product: {product_name}\n"
            f"Quantity: {quantity}\n"
            f"Address: {address}"
        )

        send_telegram_message(
            name=customer_name,
            contact=phone,
            comment=comment,
        )

        return redirect("/catalog")

    return render_template("order.html", chosen = product)

@app.route("/add_product", methods=["POST"])
def seller_product():
    product_name = request.form["product_name"]
    image_url = request.form["image_url"]
    price = request.form["price"]
    if session["user_id"] is None:
        return redirect("/")
    add_product(product_name, session["user_id"], image_url, price)
    return redirect("/catalog")

@app.route('/catalog')
def catalog():
    user = session.get('user')
    authorized = not user == None
    print(user)
    a = get_products()
    return render_template('catalog.html', logged_in=authorized, products = a)

@app.route('/seller')
def seller_page():
    return render_template('seller.html', products = selectProducts(session["user_id"]))

@app.route("/delete_product/<int:id>", methods=["POST"])
def delete_product(id):
    response = (
        supabase.table("products")
        .delete()
        .eq("id", id)
        .execute()
    )

    return redirect("/seller")


@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        add_info(user,password)
        return redirect("/")
    data = gI()
    print(data)
    return render_template("index.html", users = data)

@app.route("/exit")
def exit_page():
    session.clear()
    return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    user = request.form["username"]
    password = request.form["password"]
    user_id = verificate(user, password)
    if user_id is not None:
        session["user"] = user
        session["user_id"] = user_id
        return redirect("/catalog")
    return redirect("/")


@app.route("/delete/<int:item_id>", methods=["POST"])
def deleteItem(item_id):
    dump(item_id)
    return redirect("/")

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def editItem(item_id):
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        update(item_id, user, password)
        return redirect("/")
    return render_template("edit.html", idd=item_id)


app.run(debug = True)