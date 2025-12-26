from db_connect import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(55), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # указание на отношение (один u - один p)
    profile = db.relationship(
        'Profile',
        uselist=False,
        back_populates='user'
    )

    # указание на отношение (один u - много проектов)
    projects = db.relationship(
        'Project',
        back_populates='user'
    )

    # указание на отношение (один u - много задач)
    tasks = db.relationship(
        'Task',
        back_populates='user'
    )

class Profile(db.Model):
    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200), nullable=False)

    # зависимая таблица из 1 к 1 с внешним ключом
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        unique=True
    )

    # указание на отношение (один u - один p)
    user = db.relationship(
        'User',
        back_populates='profile'
    )

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), nullable=True)  # цвет для проекта

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    # указание на отношение (один u - много проектов)
    user = db.relationship(
        'User',
        back_populates='projects'
    )

    # указание на отношение (один проект - много задач)
    tasks = db.relationship(
        'Task',
        back_populates='project'
    )

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.String(20), nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project.id'),
        nullable=True
    )

    # указание на отношение (один u - много задач)
    user = db.relationship(
        'User',
        back_populates='tasks'
    )

    # указание на отношение (один проект - много задач)
    project = db.relationship(
        'Project',
        back_populates='tasks'
    )