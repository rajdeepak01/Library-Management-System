from flask import Flask, render_template, redirect, request
from flask import current_app as app
from .models import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

@app.route('/')
def home():
    return render_template('/landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        pwd = request.form['pwd']
        this_user = User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == pwd:
                if this_user.type == "admin":
                    return redirect('/admin')
                else:
                    return redirect(f'/user_dash/{this_user.id}')
            else:
                return render_template('login.html', msg="Invalid password try again")
        else:
            return render_template('login.html', msg="User does not exist")
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        email = request.form['email']
        user_name = User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()
        if user_name or user_email:
            return render_template("login.html", msg="User Already exist please login")
        else:
            user = User(username = username,
                        password=password,
                        email = email)
            db.session.add(user)
            db.session.commit()
        return render_template("login.html", msg="registed successfully please login buddy!")
    return render_template('register.html')

@app.route('/admin')
def admin():
    this_user = User.query.filter_by(type="admin").first()
    users = len(User.query.all())-1
    pen_ebooks = Ebook.query.filter_by(status = "pending").all()
    pen_ebooks_count = len(Ebook.query.filter_by(status = "pending").all())
    req_ebooks = Ebook.query.filter_by(status = "requested").all()
    aval = len(Ebook.query.filter_by(status = "available").all())
    grant = len(Ebook.query.filter_by(status = "granted").all())
    reqs = len(req_ebooks)
    return render_template('admin_dash.html', this_user=this_user, req_ebooks=req_ebooks,users=users, reqs=reqs, aval=aval, grant=grant, pen_ebooks=pen_ebooks,pen_ebooks_count=pen_ebooks_count)

@app.route("/user_dash/<int:user_id>")
def user_dash(user_id):
    this_user = User.query.filter_by(id = user_id).first()
    grant = Ebook.query.filter_by(status = "granted", user_id=this_user.id).all()
    req = Ebook.query.filter_by(status = "requested", user_id=this_user.id).all()
    ebook = Ebook.query.all()
    return render_template("user_dash.html", this_user=this_user, grant=grant, req=req, ebook=ebook)


@app.route('/create-ebook', methods=["GET", "POST"])
def create():
    this_user= User.query.filter_by(type="admin").first()
    if request.method == "POST":
        name = request.form.get("name")
        author = request.form.get("name")
        url = request.form.get("url")
        ebook = Ebook(name = name, author=author, url=url)
        db.session.add(ebook)
        db.session.commit()
        return redirect('/admin')
    return render_template("create_eb.html")

@app.route("/request-ebook/<int:user_id>")
def request_ebook(user_id):
    this_user = User.query.filter_by(id = user_id).first()
    ebooks = Ebook.query.filter_by(status = "available").all()
    return render_template("request.html", this_user=this_user, ebooks=ebooks)

@app.route('/request/<int:ebook_id>/<int:user_id>')
def req_eb(ebook_id, user_id):
    this_user = User.query.get(user_id)
    ebook = Ebook.query.get(ebook_id)
    ebook.status = "requested"
    ebook.user_id = user_id
    db.session.commit()
    return redirect(f"/user_dash/{this_user.id}")

@app.route('/return/<int:ebook_id>/<int:user_id>')
def return_ebook(ebook_id, user_id):
    this_user = User.query.get(user_id)
    ebook = Ebook.query.get(ebook_id)
    ebook.status = "pending"
    ebook.user_id = user_id
    db.session.commit()
    return redirect(f"/user_dash/{this_user.id}")

@app.route('/approve_return/<int:ebook_id>/<int:user_id>')
def approve_return_ebook(ebook_id, user_id):
    this_user = User.query.get(user_id)
    ebook = Ebook.query.get(ebook_id)
    ebook.status = "available"
    ebook.user_id = None
    db.session.commit()
    return redirect("/admin")


@app.route("/grant/<int:ebook_id>/<int:user_id>")
def grant_eb(ebook_id, user_id):
    this_user = User.query.get(user_id)
    ebook = Ebook.query.filter_by(id=ebook_id, user_id = user_id).first()
    ebook.status = "granted"
    ebook.user_id = user_id
    db.session.commit()
    return redirect('/admin')

@app.route("/return_approve/<int:ebook_id>/<int:user_id>")
def return_approve(ebook_id, user_id):
    this_user = User.query.get(user_id)
    ebook = Ebook.query.filter_by(id=ebook_id, user_id = user_id).first()
    ebook.status = "available"
    ebook.user_id = user_id
    db.session.commit()
    return redirect('/admin')

@app.route("/search")
def search():
    search_word = request.args.get("search")
    key = request.args.get("key")
    if key == "user":
        results = User.query.filter_by(username = search_word).all()
    else:
        results = Ebook.query.filter_by(name = search_word).all()
    return render_template("results.html", results=results, key = key)

@app.route('/view/<ebook>/<int:user_id>')
def view(ebook, user_id):
    this_user = User.query.filter_by(id = user_id).first()
    details =  Ebook.query.filter_by(user_id=user_id, name=ebook).all()
    return render_template('view.html', details=details, this_user=this_user)

@app.route("/summary")
def summary():
    this_user = User.query.filter_by(type='admin').first()
    av = len(Ebook.query.filter_by(status = "available").all())
    re = len(Ebook.query.filter_by(status = "requested").all())
    gr = len(Ebook.query.filter_by(status = "granted").all())
    pen = len(Ebook.query.filter_by(status = "pending").all())

# pie chart (generated cards)
    labels = ['available', 'requested', 'granted', "pending"]
    sizes = [av, re, gr, pen]
    colors = ['blue', 'yellow', 'green', 'pink']
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%")
    plt.title("status of ebooks")
    plt.savefig("static/pie.png")
    plt.clf()

#bar graph (requested cards)
    labels = ['available', 'requested', 'granted', "pending"]
    sizes = [av, re, gr, pen]
    plt.bar(labels, sizes)
    plt.xlabel("status of E-books")
    plt.ylabel("No of E-books")
    plt.title("Ebooks Status Distribution")
    plt.savefig("static/bar.png")
    plt.clf()

    return render_template("/summary.html", av=av, re = re, gr=gr, pen=pen, this_user=this_user)

@app.route("/user_summary/<int:user_id>")
def user_summary(user_id):
    this_user = User.query.filter_by(id = user_id).first()
    re = len(Ebook.query.filter_by(status = "requested").all())
    gr = len(Ebook.query.filter_by(status = "granted").all())

# pie chart (generated cards)
    labels = ['requested', 'granted']
    sizes = [re, gr]
    colors = ['yellow', 'green']
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%")
    plt.title("status of ebooks")
    plt.savefig("static/pie.png")
    plt.clf()

#bar graph (requested cards)
    labels = ['requested', 'granted']
    sizes = [re, gr]
    plt.bar(labels, sizes)
    plt.xlabel("status of E-books")
    plt.ylabel("No of E-books")
    plt.title("Ebooks Status Distribution")
    plt.savefig("static/bar.png")
    plt.clf()
    return render_template("/user_summary.html",re = re, gr=gr, this_user=this_user)

