import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


#: Register function
#: associates the URL /register with the register view function
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        #: validate that username and password are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                #: takes a SQL query with ? placeholders
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    #: for security, a hashing method is used for the password
                    (username, generate_password_hash(password, method="pbkdf2:sha256", salt_length=16))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


#: Login function
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        #: on this step user is queried and stored for later use
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        #: check username
        if user is None:
            error = 'Incorrect username.'
        #: check password for valid
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        #: make session
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


#: cheks if a user id is stored is the session
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


#: Logout function
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
