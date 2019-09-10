import time
from flask import Flask, redirect, url_for, request, jsonify, json
from task import task

app = Flask(__name__)


@app.route('/admin')
def hello_admin():
    return 'Hello Admin\n'


@app.route('/guest/<guest>')
def hello_guest(guest):
    return 'Hello {} as Guest\n'.format(guest)


@app.route('/user/<name>')
def hello_user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


#  curl -d '{"three":"three"}' -H 'Content-Type: application/json' -X POST http://localhost:5000/localize
@app.route('/localize', methods=['POST'])
def localize():
    data = request.get_json()   # type(data) = dict
    print(list(data.values())[0], end=' ')
    mysum = task()
    data['sum'] = mysum
    return str(data) + '\n'



if __name__ == '__main__':
    app.run(debug=True)
