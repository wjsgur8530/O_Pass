# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Card(db.Model):
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    card_type = db.Column(db.String(50))
    card_status = db.Column(db.String(50))



class Day(db.Model):
    __tablename__ = 'day'

    year = db.Column(db.ForeignKey('year.year'), primary_key=True, nullable=False)
    month = db.Column(db.ForeignKey('month.month'), primary_key=True, nullable=False, index=True)
    day = db.Column(db.Integer, primary_key=True, nullable=False)
    count = db.Column(db.Integer)

    month1 = db.relationship('Month', primaryjoin='Day.month == Month.month', backref='days')
    year1 = db.relationship('Year', primaryjoin='Day.year == Year.year', backref='days')



class MmsMsg(db.Model):
    __tablename__ = 'mms_msg'
    __table_args__ = (
        db.Index('IDX_MMS_MSG_1', 'STATUS', 'REQDATE'),
    )

    MSGKEY = db.Column(db.BigInteger, primary_key=True)
    SERIALNUM = db.Column(db.Integer)
    ID = db.Column(db.String(16))
    STATUS = db.Column(db.String(2), nullable=False, server_default=db.FetchedValue())
    PHONE = db.Column(db.String(16), nullable=False, index=True, server_default=db.FetchedValue())
    CALLBACK = db.Column(db.String(16), nullable=False, server_default=db.FetchedValue())
    TYPE = db.Column(db.String(2), nullable=False, server_default=db.FetchedValue())
    REPCNT = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    REQDATE = db.Column(db.DateTime, nullable=False)
    SENTDATE = db.Column(db.DateTime)
    RSLTDATE = db.Column(db.DateTime)
    REPORTDATE = db.Column(db.DateTime)
    RSLT = db.Column(db.String(10), server_default=db.FetchedValue())
    NET = db.Column(db.String(10))
    SUBJECT = db.Column(db.String(50), nullable=False)
    MSG = db.Column(db.String(4000))
    FILE_CNT = db.Column(db.Integer, server_default=db.FetchedValue())
    FILE_CNT_REAL = db.Column(db.Integer, server_default=db.FetchedValue())
    FILE_TYPE1 = db.Column(db.String(1))
    FILE_PATH1 = db.Column(db.String(256))
    FILE_TYPE2 = db.Column(db.String(1))
    FILE_PATH2 = db.Column(db.String(256))
    FILE_TYPE3 = db.Column(db.String(1))
    FILE_PATH3 = db.Column(db.String(256))
    FILE_TYPE4 = db.Column(db.String(1))
    FILE_PATH4 = db.Column(db.String(256))
    FILE_TYPE5 = db.Column(db.String(1))
    FILE_PATH5 = db.Column(db.String(256))
    MMS_FILE_NAME = db.Column(db.String(256))
    BAR_TYPE = db.Column(db.String(2))
    BAR_MERGE_FILE = db.Column(db.Integer)
    BAR_VALUE = db.Column(db.String(256))
    BAR_SIZE_WIDTH = db.Column(db.Integer)
    BAR_SIZE_HEIGHT = db.Column(db.Integer)
    BAR_POSITION_X = db.Column(db.Integer)
    BAR_POSITION_Y = db.Column(db.Integer)
    BAR_FILE_NAME = db.Column(db.String(256))
    ETC1 = db.Column(db.String(160))
    ETC2 = db.Column(db.String(160))
    ETC3 = db.Column(db.String(160))
    ETC4 = db.Column(db.String(160))
    ETC5 = db.Column(db.String(160))
    ETC6 = db.Column(db.String(160))
    CAMPAIGN_CODE = db.Column(db.String(20))
    ORIGIN_CID = db.Column(db.String(10))



t_mms_msg_log_202306 = db.Table(
    'mms_msg_log_202306',
    db.Column('MSGKEY', db.BigInteger, nullable=False),
    db.Column('SERIALNUM', db.Integer),
    db.Column('ID', db.String(16)),
    db.Column('STATUS', db.String(2), nullable=False, server_default=db.FetchedValue()),
    db.Column('PHONE', db.String(16), nullable=False, index=True, server_default=db.FetchedValue()),
    db.Column('CALLBACK', db.String(16), nullable=False, server_default=db.FetchedValue()),
    db.Column('TYPE', db.String(2), nullable=False, server_default=db.FetchedValue()),
    db.Column('REPCNT', db.Integer, nullable=False, server_default=db.FetchedValue()),
    db.Column('REQDATE', db.DateTime, nullable=False),
    db.Column('SENTDATE', db.DateTime),
    db.Column('RSLTDATE', db.DateTime),
    db.Column('REPORTDATE', db.DateTime),
    db.Column('RSLT', db.String(10), server_default=db.FetchedValue()),
    db.Column('NET', db.String(10)),
    db.Column('SUBJECT', db.String(50), nullable=False),
    db.Column('MSG', db.String(4000)),
    db.Column('FILE_CNT', db.Integer, server_default=db.FetchedValue()),
    db.Column('FILE_CNT_REAL', db.Integer, server_default=db.FetchedValue()),
    db.Column('FILE_TYPE1', db.String(1)),
    db.Column('FILE_PATH1', db.String(256)),
    db.Column('FILE_TYPE2', db.String(1)),
    db.Column('FILE_PATH2', db.String(256)),
    db.Column('FILE_TYPE3', db.String(1)),
    db.Column('FILE_PATH3', db.String(256)),
    db.Column('FILE_TYPE4', db.String(1)),
    db.Column('FILE_PATH4', db.String(256)),
    db.Column('FILE_TYPE5', db.String(1)),
    db.Column('FILE_PATH5', db.String(256)),
    db.Column('MMS_FILE_NAME', db.String(256)),
    db.Column('BAR_TYPE', db.String(2)),
    db.Column('BAR_MERGE_FILE', db.Integer),
    db.Column('BAR_VALUE', db.String(256)),
    db.Column('BAR_SIZE_WIDTH', db.Integer),
    db.Column('BAR_SIZE_HEIGHT', db.Integer),
    db.Column('BAR_POSITION_X', db.Integer),
    db.Column('BAR_POSITION_Y', db.Integer),
    db.Column('BAR_FILE_NAME', db.String(256)),
    db.Column('ETC1', db.String(160)),
    db.Column('ETC2', db.String(160)),
    db.Column('ETC3', db.String(160)),
    db.Column('ETC4', db.String(160)),
    db.Column('ETC5', db.String(160)),
    db.Column('ETC6', db.String(160)),
    db.Column('CAMPAIGN_CODE', db.String(20)),
    db.Column('ORIGIN_CID', db.String(10)),
    db.Index('IDX_MMS_MSG_LOG_202306_1', 'STATUS', 'REQDATE')
)



class Month(db.Model):
    __tablename__ = 'month'

    year = db.Column(db.ForeignKey('year.year'), primary_key=True, nullable=False)
    month = db.Column(db.Integer, primary_key=True, nullable=False, index=True)
    count = db.Column(db.Integer)

    year1 = db.relationship('Year', primaryjoin='Month.year == Year.year', backref='months')



class MsgPhone(db.Model):
    __tablename__ = 'msg_phone'

    MSGTYPE = db.Column(db.String(1), primary_key=True, nullable=False, server_default=db.FetchedValue())
    MSGKEY = db.Column(db.BigInteger, primary_key=True, nullable=False)
    PHONE = db.Column(db.String(16), primary_key=True, nullable=False)
    CALLBACK = db.Column(db.String(16), nullable=False)
    STATUS = db.Column(db.String(2), nullable=False, server_default=db.FetchedValue())
    RSLTDATE = db.Column(db.DateTime)
    REPORTDATE = db.Column(db.DateTime)
    RSLT = db.Column(db.String(10), server_default=db.FetchedValue())
    NET = db.Column(db.String(10))
    REPLACE_CNT = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    REPLACE_MSG = db.Column(db.String(256))



class SmsMsg(db.Model):
    __tablename__ = 'sms_msg'
    __table_args__ = (
        db.Index('IDX_SMS_MSG_1', 'STATUS', 'REQDATE'),
    )

    MSGKEY = db.Column(db.BigInteger, primary_key=True)
    REQDATE = db.Column(db.DateTime, nullable=False)
    SERIALNUM = db.Column(db.Integer)
    ID = db.Column(db.String(16))
    STATUS = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    RSLT = db.Column(db.String(2), server_default=db.FetchedValue())
    TYPE = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    REPCNT = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    PHONE = db.Column(db.String(16), nullable=False, index=True, server_default=db.FetchedValue())
    CALLBACK = db.Column(db.String(16), nullable=False, server_default=db.FetchedValue())
    RSLTDATE = db.Column(db.DateTime)
    REPORTDATE = db.Column(db.DateTime)
    MSG = db.Column(db.String(160), nullable=False)
    NET = db.Column(db.String(4))
    ETC1 = db.Column(db.String(160))
    ETC2 = db.Column(db.String(160))
    ETC3 = db.Column(db.String(160))
    ETC4 = db.Column(db.String(160))
    ETC5 = db.Column(db.String(160))
    ETC6 = db.Column(db.String(160))
    CAMPAIGN_CODE = db.Column(db.String(20))
    ORIGIN_CID = db.Column(db.String(10))



t_sms_msg_log_202306 = db.Table(
    'sms_msg_log_202306',
    db.Column('MSGKEY', db.BigInteger, nullable=False),
    db.Column('REQDATE', db.DateTime, nullable=False),
    db.Column('SERIALNUM', db.Integer),
    db.Column('ID', db.String(16)),
    db.Column('STATUS', db.String(1), nullable=False, server_default=db.FetchedValue()),
    db.Column('RSLT', db.String(2), server_default=db.FetchedValue()),
    db.Column('TYPE', db.String(1), nullable=False, server_default=db.FetchedValue()),
    db.Column('REPCNT', db.Integer, nullable=False, server_default=db.FetchedValue()),
    db.Column('PHONE', db.String(16), nullable=False, index=True, server_default=db.FetchedValue()),
    db.Column('CALLBACK', db.String(16), nullable=False, server_default=db.FetchedValue()),
    db.Column('RSLTDATE', db.DateTime),
    db.Column('REPORTDATE', db.DateTime),
    db.Column('MSG', db.String(160), nullable=False),
    db.Column('NET', db.String(4)),
    db.Column('ETC1', db.String(160)),
    db.Column('ETC2', db.String(160)),
    db.Column('ETC3', db.String(160)),
    db.Column('ETC4', db.String(160)),
    db.Column('ETC5', db.String(160)),
    db.Column('ETC6', db.String(160)),
    db.Column('CAMPAIGN_CODE', db.String(20)),
    db.Column('ORIGIN_CID', db.String(10)),
    db.Index('IDX_SMS_MSG_LOG_202306_1', 'STATUS', 'REQDATE')
)



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    department = db.Column(db.String(50))
    rank = db.Column(db.String(20))



class UserLog(db.Model):
    __tablename__ = 'user_log'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(30))
    login_timestamp = db.Column(db.DateTime)
    logout_timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)

    user = db.relationship('User', primaryjoin='UserLog.user_id == User.id', backref='user_logs')



class Visitor(db.Model):
    __tablename__ = 'visitor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    department = db.Column(db.String(30))
    phone = db.Column(db.String(30))
    manager = db.Column(db.String(30))
    device = db.Column(db.Integer)
    remarks = db.Column(db.String(50))
    object = db.Column(db.String(50))
    created_date = db.Column(db.DateTime)
    exit_date = db.Column(db.DateTime)
    exit = db.Column(db.Integer)
    approve = db.Column(db.Integer)
    location = db.Column(db.String(50))
    approve_log = db.Column(db.Integer)
    exit_log = db.Column(db.Integer)
    card_id = db.Column(db.ForeignKey('card.id'), index=True)

    card = db.relationship('Card', primaryjoin='Visitor.card_id == Card.id', backref='visitors')



class Year(db.Model):
    __tablename__ = 'year'

    year = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
