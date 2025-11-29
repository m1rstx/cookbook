from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('cookbook', __name__)


#: Function for all recipe in db "READ"
@bp.route('/')
def index():
    db = get_db()
    recipes = db.execute(
        'SELECT c.id, d_name, body, c_rule, author_id, username'
        '   FROM cookbook c JOIN user u ON c.author_id = u.id'
        '   ORDER BY c.id DESC'
    ).fetchall()
    return render_template('cookbook/index.html', recipes=recipes)


#: Single read. My first own function
@bp.route('/<int:id>/read')
def read(id):
    db = get_db()
    recipe = db.execute(
        'SELECT c.id, d_name, body, c_rule, author_id, username'
        '   FROM cookbook c JOIN user u ON c.author_id = u.id'
        '   WHERE c.id = ?',
        (id,)
    ).fetchone()

    if recipe is None:
        abort(404, f"Recipe id {id} dosen`t exist.")

    return render_template('cookbook/read.html', recipe=recipe)


#: "CREATE" function
@bp.route('/create', methods=('GET', 'POST'))
#: call wrap from auth, wrap check is user loged in
@login_required
def create():
    if request.method == 'POST':
        d_name = request.form['d_name']
        body = request.form['body']
        c_rule = request.form['c_rule']
        error = None

        if not d_name:
            error = 'Dish name is required.'
        elif not body:
            error = 'Description is required.'
        elif not c_rule:
            error = 'Cooking rule is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO cookbook (d_name, body, c_rule, author_id)'
                '   VALUES (?, ?, ?, ?)',
                (d_name, body, c_rule, g.user['id'])
            )
            db.commit()
            return redirect(url_for('cookbook.index'))

    return render_template('cookbook/create.html')


#: "UPDATE"
#: get recipe id function for update a specific record(recipe)
def get_recipe(id, check_author=True):
    recipe = get_db().execute(
        'SELECT c.id, d_name, body, c_rule, author_id, username'
        '   FROM cookbook c JOIN user u ON c.author_id = u.id'
        '   WHERE c.id = ?',
        (id,)
    ).fetchone()

    if recipe is None:
        abort(404, f"Post id {id} dosn`t exist.")

    if check_author and recipe['author_id'] != g.user['id']:
        abort(403)

    return recipe


#: "UPDATE" function
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    recipe = get_recipe(id)

    if request.method == 'POST':
        d_name = request.form['d_name']
        body = request.form['body']
        c_rule = request.form['c_rule']
        error = None

        if not d_name:
            error = 'Dish name is required.'
        elif not body:
            error = 'Description is required.'
        elif not c_rule:
            error = 'Cooking rule is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE cookbook SET d_name=?, body=?, c_rule=?'
                '   WHERE id = ?',
                (d_name, body, c_rule, id)
            )
            db.commit()
            return redirect(url_for('cookbook.index'))

    return render_template('cookbook/update.html', recipe=recipe)


#: "DELETE" function
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_recipe(id)
    db = get_db()
    db.execute('DELETE FROM cookbook WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('cookbook.index'))
