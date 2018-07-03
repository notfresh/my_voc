
class CommonModelMixin:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Word(db.Model, CommonModelMixin):
    __tablename__ = 'words'
    word = db.Column(db.String(32), index=True, nullable=False)  # 一个单词.
    interpretations = db.relationship('WordInterpretation', backref='word')



class WordInterpretation(db.Model, CommonModelMixin):
    __tablename__ = 'word_interpretation'

    WORD_TYPE = {
        'n', 'v', 'adj', 'adv', 'others', 'unknown'
    }
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), index=True )  # 一个单词的id.
    type = db.Column(db.String(8), index=True, default='unknown')
    interpretation = db.Column(db.String(1024), nullable=False)

  
class Sentence(db.Model, CommonModelMixin):
    __tablename__ = 'sentences'
    # word_id = db.Column(db.Integer, index=True)  # 一个单词的id.
    sentence = db.Column(db.String(1024), nullable=False)


class Passage(db.Model, CommonModelMixin):
    __tablename__ = 'passages'
    passage = db.Column(db.Text, nullable=False)


class WordsInSentence(db.Model, CommonModelMixin):
    __tablename__ = 'words_in_sentence'  # 一个句子出现在哪些单词里面. 反过来也可以查一个句子里包含哪些单词
    word_id = db.Column(db.Integer, index=True)  # 一个单词的id.
    sentence_id = db.Column(db.Integer, index=True)  # 一个句子的id.