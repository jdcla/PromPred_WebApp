from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager, db
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.CREATE_LIB |
                     Permission.CREATE_PLAN |
                     Permission.CREATE_SEQ, True),
            'Moderator': (Permission.WRITE_POSTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class Permission:
    CREATE_LIB = 0x01
    CREATE_PLAN = 0x02
    CREATE_SEQ = 0x04
    WRITE_POSTS = 0x08
    ADMINISTER = 0x80

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    promoter_libraries = db.relationship('Promoter_library', backref='creator_lib', lazy='dynamic')
    plan = db.relationship('Plan', backref='creator_plan', lazy='dynamic')
    sequence = db.relationship('Sequence', backref='creator_seq', lazy='dynamic')
    posts = db.relationship('Post', backref="creator_post", lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=84600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['PROMPRED_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()


    def __repr__(self):
        return '<User %r>' % (self.username)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Plan(db.Model):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    promoter_libraries = db.relationship('Promoter_library', backref='plan', lazy='dynamic')
    sequences = db.relationship('Sequence', backref='plan_seq', lazy='dynamic')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Plan {}>'.format(self.body)

class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(50))
    strength = db.Column(db.Float)
    lb_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    ub_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    library = db.Column(db.Integer, db.ForeignKey('promoter_libraries.id'))
    plan = db.Column(db.Integer, db.ForeignKey('plans.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    trans_fac_id = db.Column(db.Integer, db.ForeignKey('transcription_factors.id'))

    def __repr__(self):
        return '<Sequence {}>'.format(self.body)

class Promoter_library(db.Model):
    __tablename__ = 'promoter_libraries'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True)
    timestamp = db.Column(db.DateTime, index = True, default=datetime.utcnow)
    is_reference = db.Column(db.Boolean, default = False)
    status = db.Column(db.String(64), default="in queue")
    library_plan = db.Column(db.Integer, db.ForeignKey('plans.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sequences = db.relationship('Sequence', backref='library_seq', lazy='dynamic')

    def __repr__(self):
        return '<Prom_lib {}>'.format(self.name)

class Transcription_Factor(db.Model):
    __tablename__ = 'transcription_factors'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique=True)
    sequence = db.relationship('Transcription_Factor', backref='ref_tf', lazy='dynamic')