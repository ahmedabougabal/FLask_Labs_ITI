from flask import Flask, render_template

app = Flask(__name__)

@app.errorhandler(404)
def error_404(error):
    return render_template('errors/error.html')


@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)