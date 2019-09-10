from flask import Flask, redirect, url_for, request, jsonify
import time

app = Flask(__name__)


@app.route('/admin')
def hello_admin():
    return 'Hello Admin'


@app.route('/guest/<guest>')
def hello_guest(guest):
    return 'Hello {} as Guest'.format(guest)


@app.route('/user/<name>')
def hello_user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


@app.route('/foo', methods=['POST'])
def foo():
    data = request.json
    print(jsonify(data))


if __name__ == '__main__':
    app.run(debug=True)
