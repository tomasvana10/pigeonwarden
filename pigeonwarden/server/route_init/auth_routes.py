from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.wrappers.response import Response as WZResponse
from flask_wtf import FlaskForm
from typing import Optional
from passlib.hash import bcrypt
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


def init_auth_routes(app: Flask, users: dict[str, str], dev: bool) -> None:
    @app.before_request
    def require_login() -> Optional[WZResponse]:
        if not dev and request.endpoint not in {"login", "static"}:
            if "user" not in session:
                return redirect(url_for("login"))

        return None

    @app.route("/login", methods=["GET", "POST"])
    def login() -> WZResponse | str:
        form = LoginForm()
        if form.validate_on_submit():
            name = form.username.data
            password = form.password.data

            if name in users and bcrypt.verify(password, users[name]):
                session["user"] = name
                return redirect(url_for("index"))

            flash("Invalid username or password")

        return render_template("login.html", form=form)

    @app.route("/logout")
    def logout() -> WZResponse:
        session.pop("user", None)

        return redirect(url_for("login"))
