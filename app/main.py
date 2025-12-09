#!/usr/bin/env python
# coding=utf-8

from flask import Flask, render_template, redirect, url_for, flash
from flask import make_response

import json
import os
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import NotFound
from app.forms import UserForm

# OpenRefactory Warning: The 'Flask' method creates a Flask app
# without Cross-Site Request Forgery (CSRF) protection.
app = Flask(__name__)
CSRFProtect(app)

# Load config
app.config.from_object('app.config')

basedir = os.path.abspath(os.path.dirname(__file__))
users_path = os.path.join(basedir, "../users.json")

with open(users_path, "r") as f:
    users = json.load(f)


def save_users():
    with open(users_path, "w") as f:
        json.dump(users, f, indent=4)


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html', users=users)


@app.route("/add", methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        if username in users:
            flash(f"User {username} already exists!", "error")
        else:
            users[username] = {
                "id": form.id.data,
                "name": form.name.data,
                "description": form.description.data
            }
            save_users()
            flash(f"User {username} added successfully.", "success")
            return redirect(url_for('index'))
    return render_template('user_form.html', form=form, title="Add User", is_edit=False)


@app.route("/edit/<username>", methods=['GET', 'POST'])
def edit_user(username):
    if username not in users:
        raise NotFound

    data = users[username]
    form = UserForm(
        username=username,
        id=data['id'],
        name=data['name'],
        description=data['description']
    )

    if form.validate_on_submit():
        users[username] = {
            "id": form.id.data,
            "name": form.name.data,
            "description": form.description.data
        }
        save_users()
        flash(f"User {username} updated successfully.", "success")
        return redirect(url_for('index'))

    return render_template('user_form.html', form=form, title="Edit User", is_edit=True)


@app.route("/delete/<username>", methods=['POST'])
def delete_user(username):
    if username in users:
        del users[username]
        save_users()
        flash(f"User {username} deleted.", "success")
    return redirect(url_for('index'))


@app.route("/users", methods=['GET'])
def all_users():
    return pretty_json(users)


@app.route("/users/<username>", methods=['GET'])
def user_data(username):
    if username not in users:
        raise NotFound

    return pretty_json(users[username])


@app.route("/users/<username>/something", methods=['GET'])
def user_something(username):
    raise NotImplementedError()


def pretty_json(arg):
    response = make_response(json.dumps(arg, sort_keys=True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response


def create_test_app():
    # OpenRefactory Warning: The 'Flask' method creates a Flask app
    # without Cross-Site Request Forgery (CSRF) protection.
    app = Flask(__name__)
    CSRFProtect(app)
    return app


if __name__ == "__main__":
    app.run(port=5000)
