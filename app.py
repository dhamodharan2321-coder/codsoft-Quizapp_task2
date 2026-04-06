from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# =========================
# DATABASE SETUP
# =========================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        user_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT,
        answer TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return render_template('index.html')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')
        else:
            return "Invalid username or password"

    return render_template('login.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')
#create quiz

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Insert quiz
        c.execute("INSERT INTO quizzes (title, user_id) VALUES (?, ?)",
                  (title, session['user_id']))
        quiz_id = c.lastrowid

        questions = request.form.getlist('question[]')
        o1_list = request.form.getlist('o1[]')
        o2_list = request.form.getlist('o2[]')
        o3_list = request.form.getlist('o3[]')
        o4_list = request.form.getlist('o4[]')

        for i in range(len(questions)):
            selected = request.form.get(f'answer{i}')

            if selected == "o1":
                ans = o1_list[i]
            elif selected == "o2":
                ans = o2_list[i]
            elif selected == "o3":
                ans = o3_list[i]
            else:
                ans = o4_list[i]

            c.execute("""INSERT INTO questions 
                (quiz_id, question, option1, option2, option3, option4, answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (quiz_id,
                 questions[i],
                 o1_list[i],
                 o2_list[i],
                 o3_list[i],
                 o4_list[i],
                 ans))

        conn.commit()
        conn.close()

        return redirect('/quiz_list')

    return render_template('create_quiz.html')
# QUIZ LIST
@app.route('/quiz_list')
def quiz_list():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM quizzes")
    quizzes = c.fetchall()
    conn.close()

    return render_template('quiz_list.html', quizzes=quizzes)


# TAKE QUIZ
@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = c.fetchall()
    conn.close()

    if request.method == 'POST':
        score = 0

        for q in questions:
            qid = str(q[0])
            selected = request.form.get(qid)

            if selected == q[6]:
                score += 1

        return render_template('result.html', score=score, total=len(questions))

    return render_template('take_quiz.html', questions=questions)


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    print("Server starting...")
    app.run(debug=True)