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
# QUESTION BANK
# ======================

QUESTION_BANK = {

    "Board Exam Preparation": {

        "Mathematics": [
            {
                "id": "math1",
                "question": "Solve: 3x - 7 = 11",
                "options": ["4", "6", "8", "2"],
                "answer": "6",
                "topic": "Linear Equations"
            },
            {
                "id": "math2",
                "question": "Find the square of 12",
                "options": ["124", "144", "132", "112"],
                "answer": "144",
                "topic": "Squares"
            },
            {
                "id": "math3",
                "question": "What is sin(30°)?",
                "options": ["1", "0.5", "√3/2", "0"],
                "answer": "0.5",
                "topic": "Trigonometry"
            }
        ],

        "Physics": [
            {
                "id": "phy1",
                "question": "If velocity is constant, acceleration is?",
                "options": ["Constant", "Zero", "Increasing", "Decreasing"],
                "answer": "Zero",
                "topic": "Motion"
            },
            {
                "id": "phy2",
                "question": "Force on 3kg mass accelerating at 2 m/s²?",
                "options": ["6N", "5N", "1N", "9N"],
                "answer": "6N",
                "topic": "Newton's Laws"
            }
        ],

        "Chemistry": [
            {
                "id": "chem1",
                "question": "Atomic number represents?",
                "options": ["Neutrons", "Protons", "Mass", "Electrons only"],
                "answer": "Protons",
                "topic": "Atomic Structure"
            },
            {
                "id": "chem2",
                "question": "pH of neutral solution?",
                "options": ["0", "7", "14", "1"],
                "answer": "7",
                "topic": "Acids & Bases"
            }
        ],

        "Biology": [
            {
                "id": "bio1",
                "question": "Powerhouse of the cell?",
                "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi"],
                "answer": "Mitochondria",
                "topic": "Cell Organelles"
            },
            {
                "id": "bio2",
                "question": "Green pigment in plants?",
                "options": ["Chlorophyll", "Hemoglobin", "Melanin", "Keratin"],
                "answer": "Chlorophyll",
                "topic": "Photosynthesis"
            }
        ]

    },

    "NEET Preparation": {
        "Biology": [
            {
                "id": "neet_bio1",
                "question": "Which organelle produces ATP?",
                "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi Body"],
                "answer": "Mitochondria",
                "topic": "Cell Biology"
            }
        ]
    }
}

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
        new_user = User(
            full_name=request.form["name"],
            student_class=request.form["class"],
            board=request.form["board"],
            school=request.form["school"]
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
            user_id=1,
            subjects=",".join(selected_subjects),
            goal=goal
        )

        db.session.add(profile)
        db.session.commit()

        return redirect("/assessment")

    return render_template("subjects.html")


@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    learning_profile = LearningProfile.query.order_by(LearningProfile.id.desc()).first()

    if not learning_profile:
        return redirect("/subjects")

    subjects = learning_profile.subjects.split(",")
    goal = learning_profile.goal

    questions_to_ask = []

    if goal in QUESTION_BANK:
        for subject in subjects:
            if subject in QUESTION_BANK[goal]:
                questions_to_ask.extend(QUESTION_BANK[goal][subject])

    if request.method == "POST":

        if len(questions_to_ask) == 0:
            return redirect("/subjects")

        score = 0
        weak_topics = []

        for q in questions_to_ask:
            user_answer = request.form.get(q["id"])

            if user_answer == q["answer"]:
                score += 1
            else:
                weak_topics.append(q["topic"])

        final_score = int((score / len(questions_to_ask)) * 100)

        new_assessment = Assessment(
            user_id=1,
            subject=",".join(subjects),
            score=final_score,
            weak_area=", ".join(set(weak_topics))
        )

        db.session.add(new_assessment)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("assessment.html", questions=questions_to_ask)


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