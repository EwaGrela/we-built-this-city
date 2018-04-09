from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    make_response
)
app = Flask(__name__)

@app.route("/")
def home():
	return "Hello Kitty"

if __name__ == '__main__':
	app.run(debug=True)