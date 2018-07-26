from datetime import datetime
from app.exceptions import DataError, error_dict

from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import create_engine, Integer, Column, DateTime, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base

from config import env_config

Base = declarative_base()
db_url = env_config.get('DEV_DATABASE_URL')
engine = create_engine(db_url, echo=True)

Session = sessionmaker(bind=engine)


class CommonModelMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        dict_attr = self.__dict__
        dict_attr_public = {item[0]: item[1] for item in dict_attr.items() if not item[0].startswith('_')}  #
        return str(dict_attr_public)


class Word(CommonModelMixin, Base):
    __tablename__ = 'words'
    word = Column(String(64), index=True, nullable=False)  # 一个单词.
    interpretations = relationship('WordInterpretation', cascade='all, delete-orphan', backref=backref('word'))

    @staticmethod
    def create_word(word_str, session):
        word_str_strip = word_str.strip() if word_str else ''
        w = session.query(Word).filter(Word.word == word_str_strip).first()
        if w:
            raise DataError(10000, error_dict[10000])
        word = Word()
        word.word = word_str.strip()
        session.add(word)
        session.flush()
        return word


class WordInterpretation(CommonModelMixin, Base):
    __tablename__ = 'word_interpretation'

    WORD_TYPE = {
        'n', 'v', 'adj', 'adv', 'others', 'unknown'
    }
    word_id = Column(Integer, ForeignKey('words.id'), index=True)  # 一个单词的id.
    type = Column(String(64), index=True, default='unknown')
    interpretation = Column(String(1024), nullable=False)
    examples = relationship('WordIPEAP', cascade='all, delete-orphan', backref=backref('interpretation'))

    @staticmethod
    def create_word_interpretation(word, type, interpretation, session):
        word_interpretation = WordInterpretation()
        word_interpretation.word_id = word.id
        word_interpretation.type = type
        word_interpretation.interpretation = interpretation
        session.add(word_interpretation)
        session.flush()
        return word_interpretation


class WordIPEAP(CommonModelMixin, Base):
    __tablename__ = 'word_interpretation_examples'
    word_id = Column(Integer, ForeignKey('words.id'), index=True)  # 一个单词的id.
    interpretation_id = Column(Integer, ForeignKey('word_interpretation.id'), index=True)  # 一个单词解释的id.
    example = Column(String(1024), nullable=False)

    @staticmethod
    def create_word_ipeap(interepation_obj, example_str, session):
        example = WordIPEAP()
        example.word_id = interepation_obj.word_id
        example.interpretation_id = interepation_obj.id
        example.example = example_str
        session.add(example)
        session.flush()
        return example


class Sentence(CommonModelMixin, Base):
    __tablename__ = 'sentences'
    # word_id =Column(Integer, index=True)  # 一个单词的id. 一个句子里包含多个单词, 所以, 这里搞1对多不合适.
    sentence = Column(String(1024), nullable=False)


class Passage(CommonModelMixin, Base):
    __tablename__ = 'passages'
    passage = Column(Text, nullable=False)


class WordsInSentence(CommonModelMixin, Base):
    __tablename__ = 'words_in_sentence'  # 一个句子出现在哪些单词里面. 反过来也可以查一个句子里包含哪些单词
    word_id = Column(Integer, index=True)  # 一个单词的id.
    sentence_id = Column(Integer, index=True)  # 一个句子的id.
