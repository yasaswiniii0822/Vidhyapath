from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ======================
# DATABASE CONFIG
# ======================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vidyapath.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ======================
# DATABASE MODELS
# ======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    board = db.Column(db.String(20))
    school = db.Column(db.String(100))


class LearningProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    subjects = db.Column(db.String(200))
    goal = db.Column(db.String(100))


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    subject = db.Column(db.String(100))
    score = db.Column(db.Integer)
    weak_area = db.Column(db.String(200))


# ======================
# ROUTES
# ======================

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

        return redirect("/subjects")

    return render_template("profile.html")


@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "POST":
        selected_subjects = request.form.getlist("subjects")
        goal = request.form["goal"]

        profile = LearningProfile(
            user_id=1,  # temporary (we will fix this later properly)
            subjects=",".join(selected_subjects),
            goal=goal
        )

        db.session.add(profile)
        db.session.commit()

        return redirect("/assessment")

    return render_template("subjects.html")


@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    if request.method == "POST":
        score = 0
        weak_topics = []

        if request.form.get("q1") == "4":
            score += 1
        else:
            weak_topics.append("Algebra")

        if request.form.get("q2") == "8":
            score += 1
        else:
            weak_topics.append("Linear Equations")

        final_score = score * 50

        new_assessment = Assessment(
            user_id=1,
            subject="Mathematics",
            score=final_score,
            weak_area=", ".join(weak_topics)
        )

        db.session.add(new_assessment)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("assessment.html")


@app.route("/dashboard")
def dashboard():
    users = User.query.all()
    return render_template("dashboard.html", users=users)


# ======================
# RUN APP
# ======================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


    