from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Database URL setup
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    
    # Connection stability settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20
    }

    # db ko app ke saath initialize karein
    db.init_app(app)
    
    return app


class Result(db.Model):
    __tablename__ = 'results'
    # UniqueConstraints ko ek hi tuple mein merge kiya gaya hai
    __table_args__ = (
        db.UniqueConstraint('admission_no', 'class_name', 'exam_term', 'session', name='_admission_unique'),
        db.UniqueConstraint('class_name', 'roll_no', 'exam_term', 'session', name='_student_result_uc'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(50), nullable=True)
    roll_no = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=True)
    class_name = db.Column(db.String(20), nullable=False)
    session = db.Column(db.String(20), nullable=True)
    exam_term = db.Column(db.String(20), nullable=True)

    # Subject Marks
    hindi = db.Column(db.String(10), default="0")
    english = db.Column(db.String(10), default="0")
    maths = db.Column(db.String(10), default="0")
    science = db.Column(db.String(10), default="0")
    sst = db.Column(db.String(10), default="0")
    computer = db.Column(db.String(10), default="0")
    sanskrit = db.Column(db.String(10), default="0")
    gk = db.Column(db.String(10), default="0")
    drawing = db.Column(db.String(10), default="0")
    evs = db.Column(db.String(10), default="0")
    moral = db.Column(db.String(10), default="0")
    english_grammar = db.Column(db.String(10), default="0")
    conversation = db.Column(db.String(10), default="0")
    pt_marks = db.Column(db.String(10), default="0")
    activity = db.Column(db.String(10), default="0")
    
    total_marks = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(5), nullable=True)
    attendance = db.Column(db.String(20), nullable=True)
    rank = db.Column(db.String(10), nullable=True)

class Admission(db.Model):
    __tablename__ = 'admission'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    aadhar = db.Column(db.String(20)) # [Aadhaar Redacted]
    pen_number = db.Column(db.String(20))
    religion = db.Column(db.String(50))
    caste = db.Column(db.String(50))
    category = db.Column(db.String(20))
    admission_class = db.Column(db.String(30), nullable=False)
    last_class = db.Column(db.String(30))
    last_school = db.Column(db.String(100))
    father_education = db.Column(db.String(100))
    father_profession = db.Column(db.String(100))
    mother_education = db.Column(db.String(100))
    mother_profession = db.Column(db.String(100))
    date_submitted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Inquiry(db.Model):
    __tablename__ = 'inquiry'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    admission_class = db.Column(db.String(30), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    date_submitted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Notice(db.Model):
    __tablename__ = 'notice'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # Naya column add kiya
    image_filename = db.Column(db.String(200), nullable=True) 
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class GalleryImage(db.Model):
    __tablename__ = 'gallery_image'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200))
    category = db.Column(db.String(50), default='campus')
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Fee(db.Model):
    __tablename__ = 'fee'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(30), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)

class FeeDeposit(db.Model):
    __tablename__ = 'fee_deposit'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    class_section = db.Column(db.String(50), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    academic_session = db.Column(db.String(20), default="2026-27")
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100))
    date_submitted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)



from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy


# 2. Video Model
class Video(db.Model):
    __tablename__ = 'video'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    
    # Original URL (YouTube / FB / MP4)
    video_url = db.Column(db.Text, nullable=True)
    
    # youtube / facebook / mp4
    video_type = db.Column(db.String(50), nullable=True)
    
    # Rendered embed HTML
    embed_code = db.Column(db.Text, nullable=True)
    
    date_added = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self):
        return f"<Video {self.title}>"


class TCApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    class_section = db.Column(db.String(50), nullable=False)
    admission_number = db.Column(db.String(50), nullable=False) # Nayi field
    reason = db.Column(db.Text, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), default='Pending')     # Nayi field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BonafideRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class DownloadableDoc(db.Model):
    __tablename__ = 'downloadable_doc'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False) # e.g., "Admission Form 2026-27"
    category = db.Column(db.String(50), nullable=False, unique=True) # unique=True zaruri hai taaki ek category ki ek hi file rahe
    filename = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Doc {self.category}>'
