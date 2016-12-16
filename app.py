from flask import *
from mongoengine import *
from os import *
from werkzeug.utils import secure_filename
from datetime import *
from random import *

db_name = "hoang"
host = "ds053126.mlab.com"
port = 53126
user_name = "hoang"
password = "0986369617"

connect(db_name,
        host=host,
        port=port,
        username = user_name,
        password = password)

APP_ROOT = path.dirname(path.abspath(__file__))
UPLOADS_IMAGE = path.join(APP_ROOT, "static/image")

app = Flask(__name__)
app.config["UPLOADS_IMAGE"] = UPLOADS_IMAGE
app.config["SECRET_KEY"] = "ahihi. do's ngok's."

class product_all(Document):
    page = ListField()

class Person(Document):
    Name = StringField()
    Password = StringField()
    Contact = StringField()
    Product = ListField()

Test = {}
all_product = {}
user_fail = {"Name": "ahihi do's ngok's"}

@app.route('/profile/<name>', methods=["get","post"])
def profile(name):
    if "loggedin" in session and session["loggedin"]:
        for key in Person.objects:
            if name == key.Name:
                user = key
                break
        if "user" in session and session["user"] == name:
            if request.method == "GET":
                return render_template("profile.html", user = user)
            elif request.method == "POST":
                Name = request.form["name"]
                Price = request.form["price"]
                Type = request.form["type"]
                Image = request.files["image"]
                Description = request.form["description"]
                if Image is not None:
                    filename = secure_filename(Image.filename)
                    Image_link_real = path.join(UPLOADS_IMAGE, filename)
                    Image.save(Image_link_real)
                    Image_link_fake = "../static/image/" + filename
                    Test["Name"] = Name
                    Test["Price"] = int(Price)
                    Test["Image"] = Image_link_fake
                    Test["id"] = str(user.id) + str(randint(1,9999999999))
                    Test["Time"] = datetime.now()
                    Test["Description"] = Description
                    Test["Type"] = Type
                    user.Product.insert(0, Test)
                    user.save()
                    all_product["user_name"] = user.Name
                    all_product["user_contact"] = user.Contact
                    all_product["product_name"] = Name
                    all_product["product_price"] = int(Price)
                    all_product["product_image"] = Image_link_fake
                    all_product["Time"] = Test["Time"]
                    all_product["product_id"] = Test["id"]
                    all_product["product_description"] = Description
                    all_product["product_type"] = Test["Type"]
                    for x in product_all.objects:
                        x.page.insert(0, all_product)
                        x.save()
                    return render_template("profile.html", user = user)
        else:
            return render_template("profile_guest.html", user = user, name = session["user"])
    else:
        return redirect(url_for("login"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("homepage.html", user_list = product_all.objects[0].page[0:6])
    elif request.method == "POST":
        username = request.form["usrname"]
        password = request.form["psw"]
        for key in Person.objects:
            if username == key.Name and password == key.Password:
                session["loggedin"] = True
                user = key
                break
            else:
                session["loggedin"] = False
        if session["loggedin"]:
            session["user"] = key.Name
            return redirect(url_for("profile", name=user.Name))
        else:
            return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session["loggedin"] = False
    return redirect(url_for("index"))

@app.route('/delete/<user_id>/<product_id>')
def delete(user_id, product_id):
    for user in Person.objects:
        if str(user.id) == user_id:
            user_delete = user
            break
    for product in user_delete.Product:
        if product["id"] == product_id:
            user_delete.Product.remove(product)
            user_delete.save()
            break
    for x in product_all.objects:
        for product in x.page:
            if product["product_id"] == product_id:
                x.page.remove(product)
                x.save()
                break
    return redirect(url_for("profile", name = user.Name))

@app.route('/edit/<user_id>/<product_id>', methods=["GET", "POST"])
def edit(user_id, product_id):
    if request.method == "GET":
        return "get"
    elif request.method == "POST":
        Name = request.form["edit_name"]
        Price = request.form["edit_price"]
        for user in Person.objects:
            if str(user.id) == user_id:
                user_edit = user
                break
        for product in user_edit.Product:
            if product["id"] == product_id:
                if Name != "":
                    product["Name"] = Name
                if Price != "":
                    product["Price"] = int(Price)
                user_edit.save()
                break
        for x in product_all.objects:
            for product in x.page:
                if product["product_id"] == product_id:
                    if Name != "":
                        product["product_name"] = Name
                    if Price != "":
                        product["product_price"] = int(Price)
                    x.save()
                    break
        return redirect(url_for("profile", name = user_edit.Name))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return redirect(url_for("index"))
    elif request.method == "POST":
        username = request.form["name"]
        password = request.form["password"]
        contact = request.form["contact"]
        for key in Person.objects:
            if username == key.Name:
                session["loggedin"] = False
                break
            else:
                session["loggedin"] = True
        if session["loggedin"]:
            user = Person(Name = username, Password =password, Contact = contact, Product = [])
            user.save()
            session["user"] = user.Name
            return redirect(url_for("profile", name = username))
        else:
            return redirect(url_for("register"))

@app.route('/', methods=["GET", "POST"])
def index():
    if "loggedin" in session and session["loggedin"] and "user" in session:
        if request.method == "GET":
            return render_template("index.html", user_list = product_all.objects[0].page[0:6], name = session["user"])
        elif request.method == "POST":
            search_key_0 = request.form["search"]
            search_key = search_key_0.upper()
            search_list = search_key.split()
            Search = []
            for key_search in search_list:
                for person in product_all.objects:
                    for product in person.page:
                        product_list_0 = product['product_name'].upper()
                        product_list = product_list_0.split()
                        for key_product in product_list:
                            if key_product == key_search:
                                Search_list = product
                                if Search_list in Search:
                                    Search_result = False
                                else:
                                    Search_result = True
                                if Search_result:
                                    Search.append(Search_list)
            return render_template("index_search.html", search_list=Search, search_key=search_key_0, name = session["user"])
    else:
        if request.method == "GET":
            return render_template("homepage.html", user_list = product_all.objects[0].page[0:6])
        elif request.method == "POST":
            search_key_0 = request.form["search"]
            search_key = search_key_0.upper()
            search_list = search_key.split()
            Search = []
            for key_search in search_list:
                for person in product_all.objects:
                    for product in person.page:
                        product_list_0 = product['product_name'].upper()
                        product_list = product_list_0.split()
                        for key_product in product_list:
                            if key_product == key_search:
                                Search_list = product
                                if Search_list in Search:
                                    Search_result = False
                                else:
                                    Search_result = True
                                if Search_result:
                                    Search.append(Search_list)
            return render_template("homepage_search.html", search_list=Search, search_key=search_key_0)

@app.route('/new/<number>')
def hp_num(number):
    num = int(number)
    if "loggedin" in session and session["loggedin"] and "user" in session:
        if num == 0:
            return redirect(url_for("index", name = session["user"]))
        elif 6*(num+1) >= len(product_all.objects[0].page):
            return render_template("index_num_end.html", user_list = product_all.objects[0].page[6*num:6*(num+1)], name = session["user"] ,num =num)
        else:
            return render_template("index_num.html", user_list = product_all.objects[0].page[6*num:6*(num+1)], name = session["user"], num =num)
    else:
        if num == 0:
            return redirect(url_for("index"))
        elif 6*(num+1) >= len(product_all.objects[0].page):
            return render_template("homepage_num_end.html", user_list = product_all.objects[0].page[6*num:6*(num+1)], num =num)
        else:
            return render_template("homepage_num.html", user_list = product_all.objects[0].page[6*num:6*(num+1)], num =num)

@app.route('/nhohon30k')
def min_30k():
    if "loggedin" in session and session["loggedin"] and "user" in session:
        return render_template("index_30k.html", user_list = product_all.objects[0].page, name = session["user"])
    else:
        return render_template("homepage_30k.html", user_list = product_all.objects[0].page)

@app.route('/30kden60k')
def medium_30_60():
    if "loggedin" in session and session["loggedin"] and "user" in session:
        return render_template("index_30k_60k.html", user_list = product_all.objects[0].page, name = session["user"])
    else:
        return render_template("homepage_30k_60k.html", user_list = product_all.objects[0].page)

@app.route('/lonhon60k')
def max_60():
    if "loggedin" in session and session["loggedin"] and "user" in session:
        return render_template("index_60k.html", user_list=product_all.objects[0].page, name = session["user"])
    else:
        return render_template("homepage_60k.html", user_list = product_all.objects[0].page)


@app.route('/theloai/<name>')
def theloai(name):
    if name == "vanhoc":
        name = "Văn học"
    elif name == "tieuthuyet":
        name = "Tiểu thuyết"
    elif name == "giaotrinh":
        name = "Giáo trình"
    elif name == "tienganh":
        name = "Tiếng Anh"
    elif name == "thamkhao":
        name = "Tham khảo"
    elif name == "khac":
        name = "Khác"
    else:
        return redirect(url_for("index"))
    if "loggedin" in session and session["loggedin"] and "user" in session:
        return render_template("index_type.html", user_list=product_all.objects[0].page, name = session["user"], type = name)
    else:
        return render_template("homepage_type.html", user_list=product_all.objects[0].page, type=name)

if __name__ == '__main__':
    app.run()