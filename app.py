from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit_number():
    number = request.form['password']
    if number == "2222":
        # Run your Python script here
        try:
            subprocess.run(['python3', 'doorlock/doorlock.py'], check=True)
            print("running doorlock.py...")
            return render_template('index.html')
        except subprocess.CalledProcessError:
            return render_template('index.html')
    else:
        return "Incorrect number. Try again."


if __name__ == '__main__':
    print("Running Flask app...")
    app.run(debug=True, host='0.0.0.0')
