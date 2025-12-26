from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from db_connect import db, connect_db
import models
from sqlalchemy import func

app = Flask(__name__)
connect_db(app)

app.config['SECRET_KEY'] = 'very_secret_key'

@app.get('/set-theme/<theme>')
def set_theme(theme):
    if theme not in ['light', 'dark', 'ocean']:
        return redirect(request.referrer or url_for('main_page'))
    response = make_response(redirect(request.referrer or url_for('main_page')))
    response.set_cookie('theme', theme)
    return response


@app.get('/')
def main_page():
    return render_template('main_page.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        ex_user = models.User.query.filter_by(username=username).first()

        if ex_user:
            error = 'Логин занят'
            return render_template('register.html', error=error)

        user = models.User(
            username=username,
            password=password)

        db.session.add(user)
        db.session.commit()

        profile = models.Profile(
            user_id=user.id,
            bio="Новый пользователь")
        db.session.add(profile)
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = username

        return redirect(url_for('projects'))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = models.User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('projects'))

    return render_template('login.html')

@app.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    projects_list = models.Project.query.filter_by(user_id=user_id).all()

    tasks_without_project = models.Task.query.filter_by(
        user_id=user_id,
        project_id=None).all()

    return render_template('projects.html', projects=projects_list, tasks_without_project=tasks_without_project)

@app.route('/projects/create', methods=['POST'])
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    name = request.form['name'].strip()
    color = request.form.get('color', '#3B82F6')

    if not name:
        return redirect(url_for('projects'))

    project = models.Project(
        name=name,
        color=color,
        user_id=user_id)

    db.session.add(project)
    db.session.commit()

    return redirect(url_for('projects'))

@app.route('/projects/<int:project_id>')
def project_tasks(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    project = models.Project.query.get(project_id)

    if not project or project.user_id != session['user_id']:
        return redirect(url_for('projects'))

    tasks = models.Task.query.filter_by(project_id=project_id).all()

    todo_tasks = [t for t in tasks if t.status == 'todo']
    doing_tasks = [t for t in tasks if t.status == 'doing']
    done_tasks = [t for t in tasks if t.status == 'done']

    return render_template('project_tasks.html', project=project, todo_tasks=todo_tasks, doing_tasks=doing_tasks, done_tasks=done_tasks)

@app.route('/projects/<int:project_id>/delete')
def delete_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    project = models.Project.query.get(project_id)

    if project and project.user_id == session['user_id']:
        db.session.delete(project)
        db.session.commit()

    return redirect(url_for('projects'))

@app.route('/tasks/create', methods=['POST'])
def create_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    title = request.form['title'].strip()
    project_id = request.form.get('project_id', type=int)

    if not title:
        return redirect(request.referrer or url_for('projects'))

    task = models.Task(
        title=title,
        status='todo',
        priority='medium',
        user_id=user_id,
        project_id=project_id if project_id else None
    )

    db.session.add(task)
    db.session.commit()

    return redirect(request.referrer or url_for('projects'))

@app.route('/tasks/<int:task_id>/update', methods=['POST'])
def update_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = models.Task.query.get(task_id)

    if not task or task.user_id != session['user_id']:
        return redirect(url_for('projects'))

    task.title = request.form['title'].strip()
    task.status = request.form.get('status', 'todo')
    task.priority = request.form.get('priority', 'medium')

    project_id = request.form.get('project_id')
    if project_id:
        task.project_id = project_id if project_id != 'none' else None

    db.session.commit()
    return redirect(request.referrer or url_for('projects'))

@app.route('/tasks/<int:task_id>/delete')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = models.Task.query.get(task_id)

    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()

    return redirect(request.referrer or url_for('projects'))

@app.route('/tasks/<int:task_id>/move/<status>')
def move_task(task_id, status):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = models.Task.query.get(task_id)

    if task and task.user_id == session['user_id']:
        if status in ['todo', 'doing', 'done']:
            task.status = status
            db.session.commit()

    return redirect(request.referrer or url_for('projects'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    profile = models.Profile.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()

        if profile:
            profile.bio = bio
        else:
            profile = models.Profile(
                bio=bio,
                user_id=user_id
            )
            db.session.add(profile)

        db.session.commit()
        return redirect(url_for('profile'))

    tasks = models.Task.query.filter_by(user_id=user_id).order_by(
        models.Task.id.desc()).all()

    for task in tasks:
        if task.project_id:
            task.project = models.Project.query.get(task.project_id)
        else:
            task.project = None

    projects = models.Project.query.filter_by(user_id=user_id).all()

    return render_template('profile.html', profile=profile, tasks=tasks, projects=projects)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)