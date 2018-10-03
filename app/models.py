from datetime import datetime
import hashlib

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError, DataError, error_dict
from app import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
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


class Follow(db.Model):
    """
    关注表, 用于社交网络
    """
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 注册时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:  # 如果是管理员, 那么分配管理员角色
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:  # 如果不是管理员, 分配一个默认角色.
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:  # 根据邮箱生成一个头像hash.
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))  # 自己关注自己.

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})  # 把一个字典加密成为json字符串.

    def confirm(self, token):
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

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):  # 这个方法的作用是, 更新上次访问的时间.
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class CommonModelMixin:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        dict_attr = self.__dict__
        dict_attr_public = {item[0]: item[1] for item in dict_attr.items() if not item[0].startswith('_')} #
        return str(dict_attr_public)


class Word(CommonModelMixin, db.Model):
    __tablename__ = 'words'
    word = db.Column(db.String(64), index=True, nullable=False)  # 一个单词.
    phonetics = db.Column(db.String(64))  # 发音.
    note = db.Column(db.String(1024)) # 备注, 备注是干啥的.
    set_id = db.Column(db.Integer, index=True) # 相似或者有关联的词

    interpretations = db.relationship('WordInterpretation', cascade='all, delete-orphan', backref=db.backref('word'))

    @staticmethod
    def create_word(word_str, phonetics=None, note=None, session=None):
        if session is None:
            session = db.session
        word_str_strip = word_str.strip() if word_str else ''
        w = db.session.query(Word).filter(Word.word == word_str_strip).first()
        if w:
            raise DataError(10000, error_dict[10000])
        word = Word()
        word.word = word_str.strip()
        word.phonetics = phonetics.strip() if phonetics else ''
        word.note = note.strip() if note else ''
        session.add(word)
        session.flush()
        return word

    @staticmethod
    def update_word(word_str, word_set_id, session=None):
        if session is None:
            session = db.session
        word_str_strip = word_str.strip() if word_str else ''
        w = db.session.query(Word).filter(Word.word == word_str_strip).first()
        if w:
            w.word_set_id = word_set_id
            session.add(w)
            session.flush()
            return w
        return None


class WordInterpretation(CommonModelMixin, db.Model):
    __tablename__ = 'word_interpretation'

    WORD_TYPE = {
        'n', 'v', 'adj', 'adv', 'others', 'unknown'
    }
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), index=True)  # 一个单词的id.
    type = db.Column(db.String(64), index=True, default='unknown')
    interpretation = db.Column(db.String(1024), nullable=False)
    examples = db.relationship('WordIPEAP', cascade='all, delete-orphan', backref=db.backref('interpretation'))

    @staticmethod
    def create_word_interpretation(word, type, interpretation, session=None):
        if session is None:
            session = db.session
        word_interpretation = WordInterpretation()
        word_interpretation.word_id = word.id
        word_interpretation.type = type
        word_interpretation.interpretation = interpretation
        session.add(word_interpretation)
        session.flush()
        return word_interpretation


class WordIPEAP(db.Model, CommonModelMixin):
    __tablename__ = 'word_interpretation_examples'
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), index=True)  # 一个单词的id.
    interpretation_id = db.Column(db.Integer, db.ForeignKey('word_interpretation.id'), index=True)  # 一个单词解释的id.
    example = db.Column(db.String(1024), nullable=False)

    @staticmethod
    def create_word_ipeap(interepation_obj, example_str, session=None):
        if session is None:
            session = db.session
        example = WordIPEAP()
        example.word_id = interepation_obj.word_id
        example.interpretation_id = interepation_obj.id
        example.example = example_str
        session.add(example)
        session.flush()
        return example


class Sentence(db.Model, CommonModelMixin):
    __tablename__ = 'sentences'
    # word_id = db.Column(db.Integer, index=True)  # 一个单词的id. 一个句子里包含多个单词, 所以, 这里搞1对多不合适.
    sentence = db.Column(db.String(1024), nullable=False)


class Passage(db.Model, CommonModelMixin):
    __tablename__ = 'passages'
    passage = db.Column(db.Text, nullable=False)
    passage_html = db.Column(db.Text)
    passage_short = db.Column(db.String(1024))
    title = db.Column(db.String(128))

    @classmethod
    def create(cls, title, passage_str):
        obj = cls()
        obj.title = title
        obj.passage = passage_str
        obj.passage_short = passage_str[:300]
        db.session.add(obj)
        db.session.flush()
        return obj

    @staticmethod
    def on_changed_passage(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.passage_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Passage.passage, 'set', Passage.on_changed_passage)


class WordsInSentence(db.Model, CommonModelMixin):
    __tablename__ = 'words_in_sentence'  # 一个句子出现在哪些单词里面. 反过来也可以查一个句子里包含哪些单词
    word_id = db.Column(db.Integer, index=True)  # 一个单词的id.
    sentence_id = db.Column(db.Integer, index=True)  # 一个句子的id.


class MyWord(CommonModelMixin, db.Model):
    __tablename__ = 'mywords'  # 我的单词库
    word = db.Column(db.String(64), index=True, nullable=False)  # 一个单词.
    user_id = db.Column(db.Integer) # 谁的单词
    set_id = db.Column(db.Integer, index=True)

    @classmethod
    def create(cls, word_str, user_id=None):
        obj = cls()
        obj.word = word_str
        obj.user_id = user_id
        db.session.add(obj)
        db.session.flush()
        return obj


class WordSet(CommonModelMixin, db.Model):
    __tablename__ = 'word_set'
    set_title = db.Column(db.String(128), nullable=False)
    set_desc = db.Column(db.String(1024))

    @classmethod
    def create(cls, set_title, set_desc):
        obj = cls()
        obj.set_desc = set_desc
        obj.set_title = set_title
        db.session.add(obj)
        db.session.flush()
        return obj


class WordSetSub(CommonModelMixin, db.Model):
    __tablename__ = 'word_set_sub'
    word_id = db.Column(db.Integer, index=True)  # 一个单词的id.
    set_id = db.Column(db.Integer, index=True)  # 一个set的id.

    @classmethod
    def create(cls, word_id, set_id):
        obj = cls()
        obj.word_id = word_id
        obj.set_id = set_id
        db.session.add(obj)
        db.session.flush()
        return obj


class MyUfWord(CommonModelMixin, db.Model): # 陌生词, unfamiliar word
    __tablename__ = 'myufwords'  # 我的单词库
    word = db.Column(db.String(64), index=True, nullable=False)  # 一个单词.
    user_id = db.Column(db.Integer) # 谁的单词

    @classmethod
    def create(cls, word_str, user_id=None):
        obj = cls()
        obj.word = word_str
        obj.user_id = user_id
        db.session.add(obj)
        db.session.flush()
        return obj


class MyFavoriteWords(CommonModelMixin, db.Model):
    __tablename__ = 'my_favorite_words'
    # passage_id = db.Column(db.Integer)
    word = db.Column(db.String(64), index=True, nullable=False)  # 一个单词.
    user_id = db.Column(db.Integer, index=True, nullable=False)

    @classmethod
    def create(cls, word, user_id):
        obj = cls()
        obj.word = word
        obj.user_id = user_id
        db.session.add(obj)
        db.session.flush()
        return obj

    @classmethod
    def delete(cls, word, user_id):
        db.session.query(cls.word == word, cls.user_id == user_id).delete()
        db.session.flush()
        return 1


class MyFavoritesWordsSentences(CommonModelMixin, db.Model):
    __tablename__ = 'my_favorite_words_st'
    word = db.Column(db.String(64), index=True, nullable=False)
    passage_id = db.Column(db.Integer)
    sentence = db.Column(db.String(1024))  # a word can have difference sentences.
    user_id = db.Column(db.Integer, index=True, nullable=False)

    @classmethod
    def create(cls, user_id, word, passage_id, sentence):
        """
        收藏一个句子的收藏人，单词，文章ID，句子， 刚好形成一个完备的结构，目前先不排除重复的。相加就加
        :param user_id:
        :param word:
        :param passage_id:
        :param sentence:
        :return:
        """
        obj = cls()
        obj.user_id = user_id
        obj.word = word
        obj.passage_id = passage_id
        obj.sentence = sentence
        db.session.add(obj)
        db.session.flush()
        return obj






