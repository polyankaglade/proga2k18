from flask import Flask,request,render_template
import random

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('2.html')
    

@app.route('/count', methods=['post'])
def count():
    if 'text' in request.form:
        text = request.form['text']
        return 'Length is {0}.'.format(len(text))
    else:
        return 'U gave me no text, u bastard!'



app.run(debug=True)
