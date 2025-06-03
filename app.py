from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import google.generativeai as genai
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

genai.configure(api_key="AIzaSyAOoMLuFQYkq8uwCcu2X32xNhYxmOohH0M")
model = genai.GenerativeModel('gemini-2.0-flash')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            error = 'Username and password are required.'
        elif username == 'admin' and password == 'admin@1234':  
            session['logged_in'] = True
            return redirect(url_for('index'))
        elif username != 'admin'or password != 'admin@1234':
            if username != 'admin':
                error = 'Invalid username.'
            elif password != 'admin@1234':
                error = 'Invalid password.'
        else:
            error = 'Invalid credentials.'
    return render_template('login.html', error=error)

@app.route('/')
@login_required
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    name = request.form.get('name')
    question = request.form.get('question')
    file = request.files.get('file')
    
    if name and question and file:
        content = file.read().decode('utf-8')
        prompt = f"""Question: {question}\nContent: {content}\n\nInstructions:\nAnswer the question **only using the information provided in the content above**. Your response must meet the following criteria:\n\n1. **Answer Format**:\n- Write a clear, accurate, and concise paragraph-style answer.\n- Do not include irrelevant details, and avoid both overly short or excessively long answers.\n\n2. **Title Requirements**:\n- Every answer must begin with a **title** that summarizes the topic of the answer.\n- The title must be:\n  - **Centered** (horizontally centered on the page)\n  - In **bold**\n  - In **Times New Roman** font\n  - Font size: **18 pt**\n\n3.<br> **Examples (if applicable)**:\n- If the question asks for or implies examples, include a separate section titled:\n  - **Example:** (in bold, Times New Roman, font size 16, left-aligned)\n- Under the subtitle, list the examples one by one as follows:\n <br>  Example 1:\n     [Your example here]\n <br>  Example 2:\n     [Your second example here]\n- You may create up to two or more **relevant** and **clear** examples **on your own**, if they help clarify the answer — but ensure they align with the original content.\n\n⚠️ Important:\n- Do **not** invent or assume any information outside the given content.\n- Your output must strictly follow the format, remain accurate, and directly address the question."""
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})

    return jsonify({'response': "Missing required fields"}), 400

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
