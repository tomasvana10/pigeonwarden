from passlib.hash import bcrypt
from Flask import Flask, request, url_for, session, flash, redirect, render_template
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


def init_auth_routes(app: Flask, users: dict[str, str], dev: bool) -> None:
    @app.before_request
    def require_login():
        if not dev and request.endpoint not in {"login", "static"}:
            if "user" not in session:
                return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
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
    def logout():
        session.pop("user", None)

        return redirect(url_for("login"))
