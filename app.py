from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vidyapath.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# DATABASE MODEL
# ----------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    board = db.Column(db.String(20))
    school = db.Column(db.String(100))

# ----------------------
# ROUTES
# ----------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        name = request.form["name"]
        student_class = request.form["class"]
        board = request.form["board"]
        school = request.form["school"]

        new_user = User(
            full_name=name,
            student_class=student_class,
            board=board,
            school=school
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("profile.html")

@app.route("/dashboard")
def dashboard():
    users = User.query.all()
    return render_template("dashboard.html", users=users)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    