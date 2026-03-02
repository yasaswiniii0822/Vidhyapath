from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import json
import os
import requests

YOUTUBE_API_KEY = os.getenv("YT_API_KEY")
print("YT KEY:", YOUTUBE_API_KEY)
app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vidyapath.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

YOUTUBE_COURSES = {
    "Linear Equations": {
        "title": "Linear Equations - Full Concept",
        "channel": "Khan Academy",
        "url": "https://youtu.be/bAerID24QJ0?si=2gHrN0znAoApclhB"
    },
    "Squares": {
        "title": "Squares & Square Roots",
        "channel": "Khan Academy",
        "url": "https://youtu.be/mbc3_e5lWw0?si=XPQBcnWTM3Nw6FYL"
    },
    "Trigonometry": {
        "title": "Trigonometry Basics",
        "channel": "Physics Wallah",
        "url": "https://youtu.be/anqu3ul9WiI?si=ggWTLI2pfEw0Me8A"
    },
    "Motion": {
        "title": "Motion in One Dimension",
        "channel": "Physics Wallah",
        "url": "https://youtu.be/XIJAZM5G5Fg?si=YVIFDXMtG4TDqa_6"
    },
    "Newton's Laws": {
        "title": "Laws of Motion Explained",
        "channel": "The Organic Chemistry Tutor",
        "url": "https://youtu.be/g550H4e5FCY?si=WLTiGFYN3eXrLdZV"
    },
    "Atomic Structure": {
        "title": "Atomic Structure Complete",
        "channel": "Unacademy",
        "url": "https://www.youtube.com/live/fk_6SGKjXqI?si=_EOtyW-g6dTsQmSY"
    },
    "Acids & Bases": {
        "title": "pH & Acids Explained",
        "channel": "Khan Academy",
        "url": "https://youtu.be/J7-GewgqWUQ?si=U8o5OAsnAZB-wKjH"
    },
    "Cell Organelles": {
        "title": "Cell Organelles Explained",
        "channel": "Nucleus medical media",
        "url": "https://youtu.be/rKS-vvhMV6E?si=n1uufH4XsuEWmyfP"
    },
    "Photosynthesis": {
        "title": "Photosynthesis Process",
        "channel": "Amoeba Sisters",
        "url": "https://youtu.be/CMiPYHNNg28?si=bYAt2BViL9ujgLE5"
    }
}


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
            }
        ],
        "Chemistry": [
            {
                "id": "chem1",
                "question": "Atomic number represents?",
                "options": ["Neutrons", "Protons", "Mass", "Electrons only"],
                "answer": "Protons",
                "topic": "Atomic Structure"
            }
        ],
        "Biology": [
            {
                "id": "bio1",
                "question": "Powerhouse of the cell?",
                "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi"],
                "answer": "Mitochondria",
                "topic": "Cell Organelles"
            }
        ]
    }
}

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
    subject_breakdown = db.Column(db.Text)

def fetch_youtube_videos(query, max_results=3):
    

    if not YOUTUBE_API_KEY:
        return []  

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()

        videos = []

        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            videos.append({
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "thumbnail": snippet["thumbnails"]["medium"]["url"],
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })

        return videos

    except Exception as e:
        print("YouTube API Error:", e)
        return []

def generate_recommendations(score, weak_topics, breakdown):

    recommendations = []

    if score >= 80:
        level = "Advanced"
    elif score >= 60:
        level = "Intermediate"
    else:
        level = "Beginner"

    for topic in weak_topics:

        videos = fetch_youtube_videos(topic + " class 12 tutorial")

        if videos:
            for video in videos:
                recommendations.append({
                    "topic": topic,
                    "priority": "High",
                    "suggestion": video["title"],
                    "estimated_time": "Video Lesson",
                    "url": video["url"],
                    "channel": video["channel"],
                    "thumbnail": video["thumbnail"]
                })
        else:
            recommendations.append({
                "topic": topic,
                "priority": "High",
                "suggestion": f"Revise {topic}",
                "estimated_time": "1–2 hours",
                "url": None,
                "channel": None,
                "thumbnail": None
            })

    return {
        "level": level,
        "recommendations": recommendations
    }

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

        session["user_id"] = new_user.id
        return redirect("/subjects")

    return render_template("profile.html")


@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "POST":

        user_id = session.get("user_id")
        if not user_id:
            return redirect("/profile")

        selected_subjects = request.form.getlist("subjects")
        goal = request.form["goal"]

        profile = LearningProfile(
            user_id=user_id,
            subjects=",".join(selected_subjects),
            goal=goal
        )

        db.session.add(profile)
        db.session.commit()

        return redirect("/assessment")

    return render_template("subjects.html")


@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    user_id = session.get("user_id")
    if not user_id:
        return redirect("/profile")

    learning_profile = LearningProfile.query.filter_by(
        user_id=user_id
    ).order_by(LearningProfile.id.desc()).first()

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

        total_questions = len(questions_to_ask)
        correct = 0
        weak_topics = []

        subject_scores = {}

        for subject in subjects:
            subject_scores[subject] = {"correct": 0, "total": 0}

        for q in questions_to_ask:

            user_answer = request.form.get(q["id"])

            for subject in subjects:
                if q in QUESTION_BANK[goal].get(subject, []):
                    subject_scores[subject]["total"] += 1

                    if user_answer == q["answer"]:
                        correct += 1
                        subject_scores[subject]["correct"] += 1
                    else:
                        weak_topics.append(q["topic"])

        final_score = int((correct / total_questions) * 100) if total_questions else 0

        for subject in subject_scores:
            total = subject_scores[subject]["total"]
            correct_sub = subject_scores[subject]["correct"]

            subject_scores[subject]["percentage"] = (
                int((correct_sub / total) * 100) if total else 0
            )

        new_assessment = Assessment(
            user_id=user_id,
            subject=",".join(subjects),
            score=final_score,
            weak_area=", ".join(set(weak_topics)),
            subject_breakdown=json.dumps(subject_scores)
        )

        db.session.add(new_assessment)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("assessment.html", questions=questions_to_ask)


@app.route("/dashboard")
def dashboard():

    user_id = session.get("user_id")
    if not user_id:
        return redirect("/profile")

    # Get ALL assessments for user
    assessments = Assessment.query.filter_by(
        user_id=user_id
    ).order_by(Assessment.id.asc()).all()

    if not assessments:
        return redirect("/profile")

    latest_assessment = assessments[-1]

    score = latest_assessment.score
    weak_topics = (
        latest_assessment.weak_area.split(", ")
        if latest_assessment.weak_area
        else []
    )

    subject_breakdown = json.loads(
        latest_assessment.subject_breakdown
        if latest_assessment.subject_breakdown
        else "{}"
    )

    rec_data = generate_recommendations(score, weak_topics, subject_breakdown)

    
    scores_history = [a.score for a in assessments]
    improvement = 0

    if len(scores_history) > 1:
        improvement = scores_history[-1] - scores_history[0]

    return render_template(
        "dashboard.html",
        score=score,
        rec_data=rec_data,
        breakdown=subject_breakdown,
        scores_history=scores_history,
        improvement=improvement
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)