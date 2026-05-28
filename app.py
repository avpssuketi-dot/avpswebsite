from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
import os
import io
import urllib.parse
import pandas as pd
from functools import wraps
from werkzeug.utils import secure_filename
from sqlalchemy import func

# Cloudinary Import (Isse add karna zaroori hai!)
import cloudinary
import cloudinary.uploader

# ReportLab Imports
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ========================= App & DB Setup =========================

import os
import cloudinary
from flask import Flask
from flask_migrate import Migrate  # 1. Import Migrate
from models import db 

app = Flask(__name__)
app.secret_key = 'kuch_bhi_secret_string_yahan_likho'




# --- DATABASE CONFIGURATION ---
db_url = os.environ.get('DATABASE_URL')

# Postgres URL fix
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- CLOUDINARY CONFIGURATION ---
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'djjvsvvy8'),
    api_key = os.environ.get('CLOUDINARY_API_KEY', '465926195419728'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

# 2. DB aur Migrate ko App ke saath bind karein
db.init_app(app)
migrate = Migrate(app, db)

# 3. Models import karein
from models import Result, Admission, Notice, GalleryImage, Fee, FeeDeposit, User, Video, Inquiry, TCApplication, BonafideRequest, Admission,  Result, DownloadableDoc

# 4. Tables Create karein aur Admin setup
with app.app_context():
    db.create_all()
    
    # Admin User Initialization
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        new_admin = User(username='admin', password='123') 
        db.session.add(new_admin)
        db.session.commit()
        print("--- Admin user created successfully ---")


# ========================= SECURITY SHIELD =========================
from functools import wraps
from flask import session, redirect, url_for, flash

# 1. Decorator ko define karein
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Please login first.", "danger")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========================= MODELS =========================


class Notice(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class GalleryImage(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200))
    category = db.Column(db.String(50), default='campus') 
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Inquiry(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    admission_class = db.Column(db.String(30), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    date_submitted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Admission(db.Model):
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

class Fee(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(30), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)

class FeeDeposit(db.Model):
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

class CharacterCertificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    admission_number = db.Column(db.String(50), nullable=False)
    class_name = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='Pending')



# ========================= CONTEXT PROCESSOR =========================
@app.context_processor
def inject_global_data():
    return {
        'all_fees': Fee.query.all(),
        # Yahan se documents fetch ho rahe hain aur poori website par available hain
        'first_term': DownloadableDoc.query.filter_by(category='first_term_exam').first(),
        'half_yearly': DownloadableDoc.query.filter_by(category='half_yearly_exam').first(),
        'annual_exam': DownloadableDoc.query.filter_by(category='annual_exam').first(),
        'holiday_list': DownloadableDoc.query.filter_by(category='holiday').first(),
        'admission_form': DownloadableDoc.query.filter_by(category='admission_form').first()
    }

# ========================= MAIN WEBSITE ROUTES =========================
@app.route("/")
def home():
    # Ab home() mein sirf wahi data fetch karein jo specific homepage ke liye hai
    notices = Notice.query.order_by(Notice.date_posted.desc()).limit(5).all()
    videos = Video.query.all() 
    images = GalleryImage.query.all()
    
    # Documents pass karne ki zaroorat nahi, context_processor handle kar lega
    return render_template("index.html", notices=notices, videos=videos, images=images)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/academics")
def academics():
    return render_template("academics.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/gallery")
def gallery():
    # Saari images database se le rahe hain
    all_images = GalleryImage.query.all()
    print(f"Total images found: {len(all_images)}") 
    return render_template("gallery.html", images=all_images)



# ========================= GALLERY MANAGEMENT ROUTES =========================


@app.route("/admin/gallery", methods=['GET', 'POST'])
@login_required
def admin_gallery():
    if request.method == 'POST':
        file = request.files.get('file')
        caption = request.form.get('caption')
        category = request.form.get('category')
        
        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join('static', 'images', 'gallery')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            file.save(os.path.join(save_path, filename))
            
            new_img = GalleryImage(filename=filename, caption=caption, category=category)
            db.session.add(new_img)
            db.session.commit()
            
            # Category set ki: gallery_success
            flash("Image uploaded successfully!", "gallery_success")
            return redirect(url_for('admin_gallery'))
    
    images = GalleryImage.query.all()
    return render_template("admin/gallery.html", images=images)


@app.route("/admin/gallery/delete/<int:id>")
@login_required
def delete_gallery_image(id):
    img = GalleryImage.query.get_or_404(id)
    file_path = os.path.join('static', 'images', 'gallery', img.filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(img)
    db.session.commit()
    
    # Category set ki: gallery_success
    flash("Image deleted successfully!", "gallery_success")
    return redirect(url_for('admin_gallery'))


# ========================= VIDEO MANAGEMENT ROUTES =========================

# Helper Function (Isse route ke bahar rakhein)
def get_embed_html(url):
    if "youtube.com" in url or "youtu.be" in url:
        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("youtu.be/")[-1].split("?")[0]
        return "youtube", f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
    
    elif "facebook.com" in url or "fb.watch" in url:
        return "facebook", f'<iframe src="https://www.facebook.com/plugins/video.php?href={url}&show_text=0" width="100%" height="315" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowfullscreen></iframe>'
    
    return "mp4", f'<video width="100%" controls><source src="{url}" type="video/mp4"></video>'

# Updated Route
@app.route("/admin/media/videos", methods=['GET', 'POST'])
@login_required
def manage_videos():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        url = request.form.get('video_url', '').strip()

        if not title or not url:
            flash("Title and URL required!", "danger")
            return redirect(url_for('manage_videos'))

        video_type, embed_code = get_embed_html(url)

        try:
            new_video = Video(title=title, video_url=url, video_type=video_type, embed_code=embed_code)
            db.session.add(new_video)
            db.session.commit()
            flash("Video added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for('manage_videos'))

    videos = Video.query.order_by(Video.date_added.desc()).all()
    return render_template("admin/videos.html", videos=videos)



@app.route("/admin/media/videos/delete/<int:id>", methods=['POST'])
@login_required
def delete_video(id):

    video = Video.query.get_or_404(id)

    db.session.delete(video)
    db.session.commit()

    flash("Video deleted successfully!", "success")

    return redirect(url_for('manage_videos'))

# ========================= UPDATED NOTICE ROUTE (With Image) =========================

@app.route("/admin/notices", methods=['GET', 'POST'])
@login_required
def admin_notices():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('notice_image')
        filename = None
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            save_path = os.path.join('static', 'uploads', 'notices')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            file.save(os.path.join(save_path, filename))
        
        new_notice = Notice(title=title, content=content, image_filename=filename)
        db.session.add(new_notice)
        db.session.commit()
        
        # Category update ki: notice_success
        flash("Notice posted successfully!", "notice_success")
        return redirect(url_for('admin_notices'))
    
    # notices ko latest pehle dikhane ke liye .order_by(Notice.id.desc()) use karein
    notices = Notice.query.order_by(Notice.id.desc()).all()
    return render_template("admin/notices.html", notices=notices)


@app.route("/admin/notices/delete/<int:id>")
@login_required
def delete_notice(id):
    notice = Notice.query.get_or_404(id)
    
    # Agar image file exist karti hai toh use delete karein
    if notice.image_filename:
        file_path = os.path.join('static', 'uploads', 'notices', notice.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
    db.session.delete(notice)
    db.session.commit()
    
    # Category set ki: notice_success
    flash("Notice deleted successfully!", "notice_success")
    return redirect(url_for('admin_notices'))


# --- INQUIRY ROUTE -------------------------------------


@app.route("/submit_inquiry", methods=['POST'])
def submit_inquiry():

    print("DEBUG: Inquiry route hit hua!") # Terminal mein check karein
    print(f"DEBUG: Form data: {request.form}") # Yahan data dikhega
    try:
        # 1. Sabhi fields catch karein
        student_name = request.form.get('student_name', '').strip()
        father_name = request.form.get('father_name', '').strip()
        admission_class = request.form.get('admission_class', '').strip()
        mobile = request.form.get('mobile', '').strip()
        address = request.form.get('address', '').strip()

        # 2. Validation
        if not all([student_name, father_name, admission_class, mobile]):
            flash("Please fill all required fields!", "danger")
            return redirect(url_for('home')) # 'index' ko 'home' se badal diya

        # 3. Save
        new_inquiry = Inquiry(
            student_name=student_name, 
            father_name=father_name, 
            admission_class=admission_class, 
            mobile=mobile,
            address=address
        )
        db.session.add(new_inquiry)
        db.session.commit()
        
        flash("✅ Inquiry Submitted Successfully!", "success")
        return redirect(url_for('home')) # 'index' ko 'home' se badal diya
        
    except Exception as e:
        print(f"Error: {e}") 
        db.session.rollback()
        flash("Something went wrong. Try again.", "danger")
        return redirect(url_for('home')) # 'index' ko 'home' se badal diya




@app.route('/view_inquiries')
def view_inquiries():
    # Database se saari inquiries fetch karein
    inquiries = Inquiry.query.all()
    return render_template('admin/view_inquiries.html', inquiries=inquiries)




# --- ADMISSION ROUTE ----------------------------------------------------------------------------


@app.route("/admission", methods=['GET', 'POST'])
def admission():
    if request.method == 'POST':
        try:
            # Note: Aadhar ID is collected here as string (placeholder: [Aadhaar Redacted])
            new_admission = Admission(
                student_name=request.form.get('student_name', '').strip(),
                father_name=request.form.get('father_name', '').strip(),
                mother_name=request.form.get('mother_name', '').strip(),
                address=request.form.get('address', '').strip(),
                mobile=request.form.get('mobile', '').strip(),
                aadhar=request.form.get('aadhar', '').strip(), 
                pen_number=request.form.get('pen_number', '').strip(),
                religion=request.form.get('religion', '').strip(),
                caste=request.form.get('caste', '').strip(),
                category=request.form.get('category', '').strip(),
                admission_class=request.form.get('admission_class', '').strip(),
                last_class=request.form.get('last_class', '').strip(),
                last_school=request.form.get('last_school', '').strip(),
                father_education=request.form.get('father_education', '').strip(),
                father_profession=request.form.get('father_profession', '').strip(),
                mother_education=request.form.get('mother_education', '').strip(),
                mother_profession=request.form.get('mother_profession', '').strip()
            )

            if not all([new_admission.student_name, new_admission.father_name, new_admission.mobile]):
                flash("Please fill all required fields!", "danger")
                return redirect(url_for('admission'))

            db.session.add(new_admission)
            db.session.commit()
            flash("✅ Admission Form Submitted Successfully!", "success")
            return redirect(url_for('home'))
        except Exception:
            db.session.rollback()
            flash("Error submitting form. Please try again.", "danger")
            return redirect(url_for('admission'))
    return render_template("admission.html")


# Yeh route Admin Dashboard mein "View All" list ke liye hai
@app.route('/view_admissions')
def view_admissions():
    # Saare admissions database se nikal kar list mein dikhayein
    all_admissions = Admission.query.all()
    return render_template('admin/view_admissions.html', admissions=all_admissions)

@app.route('/view_admission_details/<int:id>')
def view_admission_details(id):
    adm = Admission.query.get_or_404(id)
    # Aap ek 'admission_details.html' file bana sakte hain jo sirf 'adm' object ko dikhaye
    return render_template('admin/admission_details.html', adm=adm)


# --- FEE MANAGEMENT ----------------------------------------------------------------------------

@app.route("/admin/fees", methods=['GET', 'POST'])
def admin_fees():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        c_name = request.form.get('class_name')
        c_amount = request.form.get('amount')
        fee = Fee.query.filter_by(class_name=c_name).first()
        if fee:
            fee.amount = c_amount
        else:
            db.session.add(Fee(class_name=c_name, amount=c_amount))
        db.session.commit()
        flash(f"Fee for {c_name} updated!", "success")
        return redirect(url_for('admin_fees')) # PRG pattern
        
    return render_template("admin/fees.html", fees=Fee.query.all())



# ========================= SECURE ADMIN ROUTES =========================

from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():

    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        from models import User
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session.clear()
            session['logged_in'] = True
            session['admin_user'] = username

            flash("Login Successful!", "success")
            return redirect(url_for('admin_dashboard'))

        flash("Invalid Credentials!", "danger")

    return render_template("admin/login.html")


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    if request.method == 'POST':

        new_password = request.form.get('new_password', '').strip()

        if not new_password:
            flash("Password required!", "danger")
            return redirect(url_for('change_password'))

        admin = User.query.filter_by(username='admin').first()

        if admin:
            admin.password = generate_password_hash(new_password)
            db.session.commit()

            flash("Password updated successfully!", "success")
            return redirect(url_for('admin_dashboard'))

        flash("Admin user not found!", "danger")

    return render_template("admin/change_password.html")



@app.route("/admin/logout")
def admin_logout():
    session.pop('logged_in', None)
    flash("You have logged out successfully.", "success")
    return redirect(url_for('home'))

@app.route('/admin/delete_result/<int:id>', methods=['POST'])
@login_required
def delete_result(id):
    res = Result.query.get_or_404(id)
    db.session.delete(res)
    db.session.commit()
    flash("Result deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))



@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    admissions = Admission.query.order_by(Admission.date_submitted.desc()).all()
    inquiries = Inquiry.query.order_by(Inquiry.date_submitted.desc()).all()
    total_notices = Notice.query.count()
    
    # Results fetch karein (Upload section ke liye)
    all_results = Result.query.all() 
    
    return render_template("admin/dashboard.html", 
                           admissions=admissions, 
                           inquiries=inquiries, 
                           total_notices=total_notices,
                           results=all_results)





@app.route("/admin/upload_results", methods=['GET', 'POST'])
@login_required
def upload_results():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                # Yahan aapki Excel mapping aayegi
                new_res = Result(
                    roll_no=str(row['Roll No']),
                    student_name=row['Name'],
                    class_name=row['Class'],
                    # ... baki subjects map karein ...
                )
                db.session.add(new_res)
            db.session.commit()
            flash("Data uploaded successfully!", "success")
    return render_template("admin/upload_results.html")


with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")

##--------------------- result route-----------------------------------------------------


# 1. SEARCH FUNCTION: Handle "1" and "1.0" mismatch
@app.route("/view_result", methods=['POST'])
def view_result():
    # Form se input
    raw_cls = request.form.get('class_name', '').strip()
    roll = request.form.get('roll_no', '').strip()
    term = request.form.get('term', '').strip()
    session = request.form.get('session', '').strip()
    
    # Class ko standardize karein
    cls = standardize_class_name(raw_cls)
    
    print(f"DEBUG: Searching for Class='{cls}', Roll='{roll}', Term='{term}', Session='{session}'")
    
    # Query: Database field aur variables match hone chahiye
    result = Result.query.filter_by(
        class_name=cls, 
        roll_no=roll, 
        exam_term=term, 
        session=session
    ).first()
    
    if not result:
        # Debugging: DB mein kya hai?
        count = Result.query.count()
        print(f"DEBUG: No result found. DB has {count} total records.")
        # Agar koi ek record dikh jaye toh format match karne mein aasani hogi
        sample = Result.query.first()
        if sample:
            print(f"DEBUG: Sample DB entry -> Class: '{sample.class_name}', Roll: '{sample.roll_no}', Term: '{sample.exam_term}'")
        
        flash("Result not found! Please check Class, Roll No, Term, and Session.", "danger")
        return redirect(url_for('results'))
    
    # Debug: Print student name to confirm result object is fetched
    print(f"DEBUG: Successfully found result for: {result.student_name}")
    
    return render_template("result_view.html", result=result)

###--------------------------------save result-----------------------------------------------


import pandas as pd

# 1. Class Name Standardizer
def standardize_class_name(raw_name):
    name = str(raw_name).lower().strip()
    
    # Pre-primary mapping
    if name in ['nursery', 'nur']: return 'nursery'
    if name in ['lkg', 'lower kg', 'kg1']: return 'lkg'
    if name in ['ukg', 'upper kg', 'kg2']: return 'ukg'
    
    # Baki classes ke liye (1-8)
    name = name.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')
    mapping = {
        '1': '1', 'i': '1', '2': '2', 'ii': '2', '3': '3', 'iii': '3',
        '4': '4', 'iv': '4', '5': '5', 'v': '5', '6': '6', 'vi': '6',
        '7': '7', 'vii': '7', '8': '8', 'viii': '8'
    }
    return mapping.get(name, name)

# 2. Database Merge Helper
def get_base_result(row, class_name, term, session):
    # Excel se roll no uthayein (Assume kiya hai index 7 par roll no hai)
    # .strip() aur string conversion se formatting errors hat jayenge
    roll_no = str(row.iloc[7]).strip() 
    
    # Database mein search karein (Roll No + Class + Term + Session)
    existing = Result.query.filter_by(
        class_name=class_name, 
        roll_no=roll_no, 
        exam_term=term, 
        session=session
    ).first()
    
    # Agar record mile toh wahi return karo (Update ke liye), warna naya
    if existing:
        return existing
        
    # Naya record banane ke liye (Admission no optional hai toh handle karein)
    adm_no = str(row.iloc[0]).strip()
    return Result(
        admission_no=adm_no, 
        roll_no=roll_no, 
        class_name=class_name, 
        exam_term=term, 
        session=session
    )
# Nayi Utility Functions jo 'AA' aur Numbers dono handle karengi
def get_val_for_calc(row, sub, mapping, term):
    start, cols = mapping[sub]
    offset = (0 if term=="1st Term" else (cols if term=="Half Yearly" else cols*2))
    total = 0
    for i in range(cols):
        val = row.iloc[start+offset+i]
        try:
            total += float(val) # Agar 'AA' hai toh ye except mein jayega
        except: continue 
    return total

def get_val_for_db(row, sub, mapping, term):
    start, cols = mapping[sub]
    offset = (0 if term=="1st Term" else (cols if term=="Half Yearly" else cols*2))
    vals = [str(row.iloc[start+offset+i]) for i in range(cols)]
    return " ".join(vals)

# 3. Main Routing
def save_results_to_db(df, class_name, term, session):
    cls = standardize_class_name(class_name)
    if cls in ['nursery', 'lkg', 'ukg']: save_pre_primary(df, cls, term, session)
    elif cls in ['1', '2']: save_primary(df, cls, term, session)
    elif cls in ['3', '4', '5']: save_middle(df, cls, term, session)
    elif cls in ['6', '7', '8']: save_high(df, cls, term, session)

# 4. Save Functions (High, Pre-Primary, Primary, Middle)
def save_high(df, class_name, term, session):
    mapping = {
        "hindi": [8, 2], "english": [14, 2], "maths": [20, 2], 
        "science": [26, 2], "sst": [32, 2], "computer": [38, 2], 
        "sanskrit": [44, 2], "gk": [50, 2], "drawing": [56, 2], 
        "eng_gram": [62, 1], "comm": [65, 1], "pt": [68, 1], "activity": [71, 1]
    }
    
    for _, row in df.iterrows():
        # 1. Roll No ko safe tareeke se handle karein (NaN error fix)
        val = row.iloc[7]
        if pd.isna(val): continue
        try:
            raw_roll = str(int(float(val)))
        except (ValueError, TypeError):
            continue # Agar roll no valid nahi hai toh skip karein
            
        # 2. Database mein record check karein
        res = Result.query.filter_by(
            class_name=class_name, 
            roll_no=raw_roll, 
            exam_term=term, 
            session=session
        ).first()
        
        # 3. Agar naya hai toh object banayein
        if not res:
            res = Result(
                class_name=class_name,
                roll_no=raw_roll,
                exam_term=term,
                session=session
            )
        
        # 4. Fields Update
        res.admission_no = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        res.student_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        res.father_name = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
        
        # 5. Marks Update (Saare 13 subjects)
        res.hindi = get_val_for_db(row, "hindi", mapping, term)
        res.english = get_val_for_db(row, "english", mapping, term)
        res.maths = get_val_for_db(row, "maths", mapping, term)
        res.science = get_val_for_db(row, "science", mapping, term)
        res.sst = get_val_for_db(row, "sst", mapping, term)
        res.computer = get_val_for_db(row, "computer", mapping, term)
        res.sanskrit = get_val_for_db(row, "sanskrit", mapping, term)
        res.gk = get_val_for_db(row, "gk", mapping, term)
        res.drawing = get_val_for_db(row, "drawing", mapping, term)
        res.english_grammar = get_val_for_db(row, "eng_gram", mapping, term)
        res.conversation = get_val_for_db(row, "comm", mapping, term)
        res.pt_marks = get_val_for_db(row, "pt", mapping, term)
        res.activity = get_val_for_db(row, "activity", mapping, term)
        
        # 6. Total Calculation
        res.total_marks = sum([get_val_for_calc(row, sub, mapping, term) for sub in mapping])
        
        # 7. Merge (Ye Insert/Update dono handle karega)
        db.session.merge(res)
    
    db.session.commit()


def save_pre_primary(df, class_name, term, session):
    mapping = {"hindi": [8, 2], "english": [14, 2], "maths": [20, 2], "gk": [17, 1], "drawing": [20, 1], "comm": [23, 1], "pt": [26, 1], "activity": [30, 1]}
    for _, row in df.iterrows():
        if pd.isna(row.iloc[7]) or str(row.iloc[7]).lower() in ['roll no', 'nan', '']: continue
        res = get_base_result(row, class_name, term, session)
        res.roll_no, res.student_name, res.father_name = str(int(float(row.iloc[7]))), str(row.iloc[1]), str(row.iloc[2])
        res.hindi = get_val_for_db(row, "hindi", mapping, term)
        res.english = get_val_for_db(row, "english", mapping, term)
        res.maths = get_val_for_db(row, "maths", mapping, term)
        res.gk = get_val_for_db(row, "gk", mapping, term)
        res.drawing = get_val_for_db(row, "drawing", mapping, term)
        res.conversation = get_val_for_db(row, "comm", mapping, term)
        res.pt_marks = get_val_for_db(row, "pt", mapping, term)
        res.activity = get_val_for_db(row, "activity", mapping, term)
        res.total_marks = sum([get_val_for_calc(row, sub, mapping, term) for sub in mapping])
        db.session.merge(res)
    db.session.commit()

def save_primary(df, class_name, term, session):
    mapping = {"hindi": [8, 2], "english": [14, 2], "maths": [20, 2], "evs": [26, 2], "sanskrit": [32, 2], "drawing": [38, 1], "moral": [41, 1], "comm": [44, 1], "pt": [47, 1], "activity": [50, 1]}
    for _, row in df.iterrows():
        if pd.isna(row.iloc[7]) or str(row.iloc[7]).lower() in ['roll no', 'nan', '']: continue
        res = get_base_result(row, class_name, term, session)
        res.roll_no, res.student_name, res.father_name = str(int(float(row.iloc[7]))), str(row.iloc[1]), str(row.iloc[2])
        res.hindi = get_val_for_db(row, "hindi", mapping, term)
        res.english = get_val_for_db(row, "english", mapping, term)
        res.maths = get_val_for_db(row, "maths", mapping, term)
        res.evs = get_val_for_db(row, "evs", mapping, term)
        res.sanskrit = get_val_for_db(row, "sanskrit", mapping, term)
        res.drawing = get_val_for_db(row, "drawing", mapping, term)
        res.moral = get_val_for_db(row, "moral", mapping, term)
        res.conversation = get_val_for_db(row, "comm", mapping, term)
        res.pt_marks = get_val_for_db(row, "pt", mapping, term)
        res.activity = get_val_for_db(row, "activity", mapping, term)
        res.total_marks = sum([get_val_for_calc(row, sub, mapping, term) for sub in mapping])
        db.session.merge(res)
    db.session.commit()

def save_middle(df, class_name, term, session):
    mapping = {"hindi": [8, 2], "english": [14, 2], "maths": [20, 2], "evs": [26, 2], "computer": [32, 2], "sanskrit": [38, 2], "gk": [44, 2], "drawing": [50, 2], "comm": [56, 1], "pt": [59, 1], "eng_gram": [62, 1], "activity": [65, 1]}
    for _, row in df.iterrows():
        if pd.isna(row.iloc[7]) or str(row.iloc[7]).lower() in ['roll no', 'nan', '']: continue
        res = get_base_result(row, class_name, term, session)
        res.roll_no, res.student_name, res.father_name = str(int(float(row.iloc[7]))), str(row.iloc[1]), str(row.iloc[2])
        res.hindi = get_val_for_db(row, "hindi", mapping, term)
        res.english = get_val_for_db(row, "english", mapping, term)
        res.maths = get_val_for_db(row, "maths", mapping, term)
        res.evs = get_val_for_db(row, "evs", mapping, term)
        res.computer = get_val_for_db(row, "computer", mapping, term)
        res.sanskrit = get_val_for_db(row, "sanskrit", mapping, term)
        res.gk = get_val_for_db(row, "gk", mapping, term)
        res.drawing = get_val_for_db(row, "drawing", mapping, term)
        res.conversation = get_val_for_db(row, "comm", mapping, term)
        res.pt_marks = get_val_for_db(row, "pt", mapping, term)
        res.english_grammar = get_val_for_db(row, "eng_gram", mapping, term)
        res.activity = get_val_for_db(row, "activity", mapping, term)
        res.total_marks = sum([get_val_for_calc(row, sub, mapping, term) for sub in mapping])
        db.session.merge(res)
    db.session.commit()

######## -----------show result----------------------------------------------------------


@app.route('/result/<roll_no>')
def show_result(roll_no):
    # Us roll no ke saare records nikaal lein
    student_results = Result.query.filter_by(roll_no=roll_no).all()
    if not student_results:
        flash("Result not found!")
        return redirect(url_for('home'))
        
    return render_template('result_view.html', results=student_results)



@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required
def upload_result():
    if request.method == 'POST':
        file = request.files.get('file')
        raw_class = request.form.get('class_name')
        term = request.form.get('term')
        session = request.form.get('session')
        
        def normalize(val):
            # Sabse pehle input ko string mein badlein aur saaf karein
            val = str(val).lower().replace('th', '').replace('st', '').replace('nd', '').replace('rd', '').replace('class', '').strip()
            # Roman numerals handle karein
            roman = {'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5', 'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9', 'x': '10'}
            return roman.get(val, val)

        norm_class = normalize(raw_class)
        
        if not file or not raw_class or not term or not session:
            flash("Sabhi fields bharein!", "danger")
            return redirect(request.url)
        
        try:
            df = pd.read_excel(file, header=None, skiprows=5)
            # DataFrame mein class column ko normalize karein (Index 5 assume kiya hai)
            df['norm_col'] = df.iloc[:, 5].apply(normalize)
            df_filtered = df[df['norm_col'] == norm_class].copy()
            
            if df_filtered.empty:
                flash(f"Error: Is class ({norm_class}) ka koi data nahi mila!", "danger")
                return redirect(request.url)
            
            # 1. DELETE: Purana data saaf karein (Database error rokne ke liye)
            db.session.execute(
                db.text("DELETE FROM results WHERE class_name = :cls AND exam_term = :term AND session = :sess"),
                {"cls": str(norm_class), "term": str(term), "sess": str(session)}
            )
            
            # 2. SAVE: Class ke hisaab se sahi function call karein
            if norm_class in ['6', '7', '8']:
                save_high(df_filtered, norm_class, term, session)
            else:
                save_results_to_db(df_filtered, norm_class, term, session)
            
            db.session.commit()
            flash(f"Success! Class {norm_class} ka data update ho gaya.", "success")
            
        except Exception as e:
            db.session.rollback()
            # Error ko terminal mein saaf dikhayein
            print(f"CRITICAL ERROR: {str(e)}") 
            flash(f"Error: {str(e)}", "danger")
            
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_upload.html')


@app.route("/admin/delete_all_results", methods=['POST'])
@login_required
def delete_all_results():
    try:
        Result.query.delete() 
        db.session.commit()
        flash("All results deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting results.", "danger")
    return redirect(url_for('admin_dashboard'))


@app.route('/check_db')
def check_db():
    results = Result.query.all()
    output = []
    for r in results:
        # Yahan se check karein ki DB mein actual data kya hai
        output.append(f"Class: '{r.class_name}', Roll: '{r.roll_no}', Term: '{r.exam_term}', Session: '{r.session}'")
    return "<br>".join(output) if output else "Database khali hai!"

# ========================= ADMISSION FORM DOWNLOAD ROUTE =========================


@app.route("/download_admission_form", defaults={'student_id': None})
@app.route("/download_admission_form/<int:student_id>")
def download_admission_form(student_id):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    if student_id:
        student = Admission.query.get_or_404(student_id)
        form_no = str(student.id)
        submit_date = student.date_submitted.strftime('%d-%m-%Y')
        student_name = student.student_name.upper()
        pen_no = student.pen_number or "________"
        adm_class = student.admission_class
        last_class = student.last_class or "________"
        religion = student.religion or "________"
        category = student.category or "________"
        caste = student.caste or "________"
        aadhar = student.aadhar or "________"
        last_school = (student.last_school or "______________________________").upper()
        
        father_name = student.father_name.upper()
        mother_name = student.mother_name.upper()
        father_edu = student.father_education or "________________"
        mother_edu = student.mother_education or "________________"
        father_prof = student.father_profession or "________________"
        mother_prof = student.mother_profession or "________________"
        mobile = student.mobile
        address = student.address.upper()
    else:
        form_no = "________"
        submit_date = "________"
        student_name = "______________________________"
        pen_no = "________"
        adm_class = "________"
        last_class = "________"
        religion = "________"
        category = "________"
        caste = "________"
        aadhar = "________"
        last_school = "______________________________"
        father_name = "____________________"
        mother_name = "____________________"
        father_edu = "________________"
        mother_edu = "________________"
        father_prof = "________________"
        mother_prof = "________________"
        mobile = "________________"
        address = "________________________________________________"

    try:
        c.setLineWidth(1.5)
        c.setStrokeColor(colors.HexColor("#1f4e79"))
        c.rect(0.8*cm, 0.8*cm, width-1.6*cm, height-1.6*cm)

        logo_path = os.path.join("static", "images", "logo.jpg")
        if not os.path.exists(logo_path): logo_path = os.path.join("static", "images", "logo.png")
        if os.path.exists(logo_path): c.drawImage(logo_path, 1.2*cm, height-3.0*cm, 2.0*cm, 2.0*cm, preserveAspectRatio=True)

        c.setFillColor(colors.HexColor("#1f4e79"))
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width/2 + 0.5*cm, height-2.0*cm, "ANGELS VALLEY PUBLIC SCHOOL")
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2 + 0.5*cm, height-2.6*cm, "(Indrani Nagar Suketi - Fatehpur)")
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2 + 0.5*cm, height-3.6*cm, "ADMISSION FORM")

        c.rect(width-3.6*cm, height-5.2*cm, 2.4*cm, 2.8*cm)

        c.setFillColor(colors.HexColor("#1f4e79"))
        c.rect(1.2*cm, height-6.3*cm, width-2.4*cm, 0.7*cm, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width/2, height-6.1*cm, "STUDENT DETAILS")

        data1 = [
            ["FORM NO:", form_no, "ADM. DATE:", submit_date],
            ["STUDENT NAME:", student_name, "PEN NO:", pen_no],
            ["DATE OF BIRTH:", "________", "GENDER:", "________"],
            ["DOB IN WORDS:", "______________________________", "", ""],
            ["ADM. CLASS:", adm_class, "LAST CLASS:", last_class],
            ["RELIGION:", religion, "CATEGORY:", category],
            ["CASTE:", caste, "AADHAR NO:", aadhar],
            ["LAST SCHOOL:", last_school, "", ""],
            ["NATIONALITY:", "INDIAN", "BLOOD GROUP:", "________"]
        ]

        col_ws = [4*cm, 5.3*cm, 4*cm, 5.3*cm]
        t = Table(data1, colWidths=col_ws, rowHeights=0.7*cm)
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f2f2f2")),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#f2f2f2")),
            ('SPAN', (1,1), (3,1)), ('SPAN', (1,3), (3,3)), ('SPAN', (1,7), (3,7)),
        ]))
        t.wrapOn(c, width, height)
        t.drawOn(c, 1.2*cm, height-13.0*cm)

        c.setFillColor(colors.HexColor("#1f4e79"))
        c.rect(1.2*cm, height-14.0*cm, width-2.4*cm, 0.7*cm, fill=1)
        c.setFillColor(colors.white)
        c.drawCentredString(width/2, height-13.75*cm, "FAMILY & CONTACT DETAILS")

        data2 = [
            ["FATHER'S NAME:", father_name, "MOTHER'S NAME:", mother_name],
            ["FATHER EDU.:", father_edu, "MOTHER EDU.:", mother_edu],
            ["FATHER PROF.:", father_prof, "MOTHER PROF.:", mother_prof],
            ["MOBILE NO:", mobile, "STUDENT AADHAR:", "________________"],
            ["FULL ADDRESS:", address, "", ""]
        ]

        t2 = Table(data2, colWidths=col_ws, rowHeights=0.7*cm)
        t2.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f2f2f2")),
            ('SPAN', (1,4), (3,4)),
        ]))
        t2.wrapOn(c, width, height)
        t2.drawOn(c, 1.2*cm, height-18.2*cm)

        c.setFillColor(colors.HexColor("#1f4e79"))
        c.rect(1.2*cm, height-19.2*cm, width-2.4*cm, 0.7*cm, fill=1)
        c.setFillColor(colors.white)
        c.drawCentredString(width/2, height-18.95*cm, "PARENT'S DECLARATION")

        styles = getSampleStyleSheet()
        p = Paragraph("I hereby declare that all information furnished is true to the best of my knowledge. I agree to abide by school discipline.", styles["BodyText"])
        p.wrapOn(c, width-3.5*cm, 3*cm)
        p.drawOn(c, 1.5*cm, height-21.0*cm)

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawCentredString(4*cm, 3.5*cm, "PARENT'S SIGN")
        c.drawCentredString(width/2, 3.5*cm, "ADMIN SIGN")
        c.drawCentredString(width-4*cm, 3.5*cm, "PRINCIPAL SIGN")

        c.save()
        buffer.seek(0)
        filename = f"Admission_Form_{student_name.replace(' ', '_')}.pdf" if student_id else "Admission_Form_Blank.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        return f"Error: {str(e)}", 500


# ========================= NAYA ROUTE: QUICK INQUIRY SLIP PDF =========================

@app.route("/admin/download_inquiry/<int:inquiry_id>")
@login_required
def download_inquiry_slip(inquiry_id):
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    try:
        # Mini elegant border
        c.setLineWidth(1)
        c.setStrokeColor(colors.HexColor("#d32f2f"))
        c.rect(1*cm, height/2, width-2*cm, height/2 - 1*cm)

        # Header
        c.setFillColor(colors.HexColor("#1f4e79"))
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height - 2*cm, "ANGELS VALLEY PUBLIC SCHOOL")
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, height - 2.5*cm, "Admission Inquiry Slip (Session 2026-27)")

        # Box Details Title
        c.setFillColor(colors.HexColor("#d32f2f"))
        c.rect(1.5*cm, height - 4*cm, width-3*cm, 0.6*cm, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, height - 3.6*cm, "INQUIRY DETAILS")

        # Dynamic Data
        data = [
            ["Inquiry ID:", f"ENQ-{inquiry.id}", "Date Received:", inquiry.date_submitted.strftime('%d-%m-%Y')],
            ["Student Name:", inquiry.student_name.upper(), "Seeking Class:", inquiry.admission_class],
            ["Father's Name:", inquiry.father_name.upper(), "Contact Number:", inquiry.mobile]
        ]
        
        t = Table(data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm], rowHeights=0.8*cm)
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ]))
        t.wrapOn(c, width, height)
        t.drawOn(c, 1.5*cm, height - 7*cm)

        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.grey)
        c.drawString(1.5*cm, height - 8*cm, "* This is a quick office copy. Please follow up with parents within 24 hours.")

        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"Inquiry_Slip_{inquiry.student_name}.pdf", mimetype='application/pdf')
    except Exception as e:
        return f"Error: {str(e)}", 500



#----------------------------- Rest of the Routes ------------------------------------------------------

@app.route('/tc_application', methods=['GET', 'POST'])
def tc_application():
    if request.method == 'POST':
        # Yahan 'admission_number' zaroor add karein
        new_app = TCApplication(
            student_name = request.form.get('student_name'),
            father_name = request.form.get('father_name'),
            class_section = request.form.get('class_section'),
            admission_number = request.form.get('admission_number'), # YEH ADD KAREIN
            reason = request.form.get('reason'),
            mobile = request.form.get('mobile'),
            status = 'Pending' # Status bhi add kar dein
        )
        db.session.add(new_app)
        db.session.commit()
        flash("TC Application Submitted!", "success")
        return redirect(url_for('tc_application'))
    
    return render_template('tc_application.html', is_admin=False)




@app.route("/character_certificate", methods=['GET', 'POST'])
def character_certificate():
    if request.method == 'POST':
        # Database logic
        new_req = CharacterCertificate(
            student_name = request.form.get('student_name'),
            father_name = request.form.get('father_name'),
            admission_number = request.form.get('admission_number'),
            class_name = request.form.get('class_name'),
            reason = request.form.get('reason'),
            status = 'Pending'
        )
        db.session.add(new_req)
        db.session.commit()
        
        flash("✅ Application Submitted Successfully!", "success")
        return redirect(url_for('character_certificate'))
    
    # YEH LINE ZAROORI HAI: Ye tab chalegi jab page pehli baar load hoga
    return render_template("character_certificate.html")
    

# 1. View Requests ka route
@app.route('/view_character_requests')
def view_character_requests():
    # Database se saari requests uthayein
    requests = CharacterCertificate.query.all()
    # Path 'admin/view_character.html' set kiya hai
    return render_template('admin/view_character.html', requests=requests)

# 2. Status Update karne ka route (Buttons ke liye)
@app.route('/update_character_status/<int:id>/<new_status>')
def update_character_status(id, new_status):
    # Specific record fetch karein
    request_data = CharacterCertificate.query.get_or_404(id)
    # Status change karein
    request_data.status = new_status
    # Database mein save karein
    db.session.commit()
    # Wapas list page par bhejein
    return redirect(url_for('view_character_requests'))




@app.route('/bonafide', methods=['GET', 'POST'])
def bonafide():
    if request.method == 'POST':
        # Debugging: terminal mein check karein ki data aa raha hai ya nahi
        student_name = request.form.get('student_name')
        father_name = request.form.get('father_name')
        class_name = request.form.get('class_name') # HTML ka 'name' yahan hona chahiye
        purpose = request.form.get('purpose')
        mobile = request.form.get('mobile')
        
        # Agar class_name phir bhi None hai, toh ye check karke handle karein
        if not class_name:
            flash("Error: Class field is missing!", "danger")
            return redirect(url_for('bonafide'))

        new_req = BonafideRequest(
            student_name=student_name,
            father_name=father_name,
            class_name=class_name,
            purpose=purpose,
            mobile=mobile
        )
        db.session.add(new_req)
        db.session.commit()
        
        flash("✅ Bonafide Request Submitted Successfully!", "success")
        return redirect(url_for('bonafide'))
    
    return render_template('bonafide.html', is_admin=False)




@app.route("/prospectus")
def prospectus(): return render_template("prospectus.html")

@app.route('/results')
def results():
    return render_template('results.html')

# --- TC Applications Admin View -------------------------------------------------------------------------------------------


@app.route('/view_tc_applications')
def view_tc_applications():
    # Admin ke liye list fetch karein
    tc_apps = TCApplication.query.all() 
    return render_template('tc_application.html', tc_apps=tc_apps, is_admin=True)

@app.route('/update_tc_status/<int:id>/<new_status>')
def update_tc_status(id, new_status):
    tc_app = TCApplication.query.get_or_404(id)
    tc_app.status = new_status
    db.session.commit()
    flash(f"TC request updated to {new_status}!", "success")
    return redirect(url_for('view_tc_applications'))


# --- Bonafide Requests Admin View ---
@app.route('/view_bonafide_requests')
def view_bonafide_requests():
    # Admin ke liye list fetch karein
    bonafide_reqs = BonafideRequest.query.all()
    return render_template('bonafide.html', bonafide_reqs=bonafide_reqs, is_admin=True)



#########------------Fee deposit --------------------------------



# FEE DEPOSIT FUNCTIONAL ROUTE (Check: Ye upar wala hata kar yahi ek version rakhein)
@app.route("/fee_deposit", methods=['GET', 'POST'])
def fee_deposit():
    if request.method == 'POST':
        try:
            new_payment = FeeDeposit(
                student_name=request.form.get('student_name'),
                father_name=request.form.get('father_name'),
                class_section=request.form.get('class_section'),
                month=request.form.get('month'),
                amount=float(request.form.get('amount', 0)),
                transaction_id=request.form.get('transaction_id')
            )
            db.session.add(new_payment)
            db.session.commit()
            flash("Payment details submitted successfully plz go to download section to download reciept!", "success")
            return redirect(url_for('fee_deposit'))
        except Exception:
            db.session.rollback()
            flash("Error in payment submission.", "danger")
    return render_template("fee_deposit.html")

@app.errorhandler(404)
def page_not_found(e): return render_template("404.html"), 404




@app.route("/send-whatsapp/<int:deposit_id>")
def send_whatsapp(deposit_id):
    deposit = FeeDeposit.query.get_or_404(deposit_id)
    
    # Message ka content
    msg = f"""*एंजल्स वैली पब्लिक स्कूल, सुकेती* ✅
    
    *विद्यार्थी का नाम:* {deposit.student_name}
    *फीस प्राप्त हुई:* ₹{deposit.amount:,.0f}
    *महीना:* {deposit.month}
    *दिनांक:* {deposit.date_submitted.strftime('%d-%m-%Y')}
    
    आपके भुगतान के लिए धन्यवाद! 🙏
    *एंजल्स वैली पब्लिक स्कूल*"""
    
    encoded_msg = urllib.parse.quote(msg)
    
    # Web par WhatsApp kholne ka URL
    # Agar mobile number database mein hai toh use karein, nahi toh sirf link open karein
    whatsapp_url = f"https://wa.me/?text={encoded_msg}"
    
    return redirect(whatsapp_url)


###------------------------------ fee structure -------------------------------


@app.route("/fee_structure")
def fee_structure():
    # Saari fees fetch karo aur page ko bhejo
    all_fees = Fee.query.all()
    return render_template("fee_structure.html", fees=all_fees)

@app.route("/receipt_search", methods=['GET', 'POST'])
def receipt_search():
    deposit = None # HTML mein hum 'deposit' variable use kar rahe hain
    if request.method == 'POST':
        # Form ke 'name' attribute se data lein
        search_query = request.form.get('transaction_id') 
        
        if search_query:
            # FeeDeposit model mein search karein
            deposit = FeeDeposit.query.filter(
                (FeeDeposit.transaction_id == search_query) | 
                (FeeDeposit.student_name == search_query)
            ).first()
            
            if not deposit:
                flash("No receipt found with this ID or Name!", "danger")
            else:
                flash("Receipt found successfully!", "success")
                
    return render_template("receipt_search.html", deposit=deposit)


# ========================= MANUAL SYNC ROUTE =========================
@app.route("/admin/manual-sync")
@login_required
def manual_sync():
    # Yahan aap apna sync ka logic likh sakte hain
    flash("ERP Data Sync Started...", "info")
    return redirect(url_for('admin_dashboard'))

# ========================= VIEW DEPOSITS ROUTE =========================

@app.route("/admin/view-deposits")
@login_required
def view_deposits():
    # Saare deposits fetch karein
    deposits = FeeDeposit.query.order_by(FeeDeposit.date_submitted.desc()).all()
    # Total calculation (sum)
    total_amount = db.session.query(func.sum(FeeDeposit.amount)).scalar() or 0
    return render_template("admin/view_deposits.html", deposits=deposits, total=total_amount)



#####----------------------- download fee reciept---------------------------------


@app.route("/download_fee_receipt/<int:deposit_id>")
def download_receipt(deposit_id):
    deposit = FeeDeposit.query.get_or_404(deposit_id)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=(400, 500)) # Receipt ka size chota rakha hai
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(200, 460, "ANGELS VALLEY PUBLIC SCHOOL")
    p.setFont("Helvetica", 10)
    p.drawCentredString(200, 445, "Indrani Nagar, Suketi - Fatehpur")
    p.line(50, 435, 350, 435) # Seperator line
    
    # Details
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 410, "FEE PAYMENT RECEIPT")
    
    p.setFont("Helvetica", 11)
    y = 380
    data = [
        ("Student Name:", deposit.student_name),
        ("Father's Name:", deposit.father_name),
        ("Class/Section:", deposit.class_section),
        ("Fee Month:", f"{deposit.month} ({deposit.academic_session})"),
        ("Amount Paid:", f"₹ {deposit.amount}"),
        ("Transaction ID:", deposit.transaction_id),
        ("Payment Date:", deposit.date_submitted.strftime('%d-%m-%Y'))
    ]
    
    for label, value in data:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(60, y, label)
        p.setFont("Helvetica", 11)
        p.drawString(180, y, str(value))
        y -= 25
    
    # Footer
    p.line(50, 150, 350, 150)
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(200, 130, "This is a computer generated receipt.")
    p.drawCentredString(200, 115, "Thank you for your payment!")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Receipt_{deposit.student_name}.pdf", mimetype='application/pdf')

@app.route('/admin/delete_fee/<int:id>', methods=['POST'])
@login_required
def delete_fee(id):
    fee = Fee.query.get_or_404(id)
    db.session.delete(fee)
    db.session.commit()
    flash("Fee deleted successfully!", "success")
    return redirect(url_for('admin_fees')) # Ya jahan aapko redirect karna ho


#--------------------admin docs upload----------------------------------------

# 1. Manage Downloads (Upload/Update)
@app.route("/admin/docs", methods=['GET', 'POST'])
@login_required
def admin_docs():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        file = request.files.get('file')
        
        if file and title and category:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.root_path, 'static', 'uploads', 'docs')
            if not os.path.exists(save_path): os.makedirs(save_path)
            
            # Purana record delete (Replace logic)
            old_doc = DownloadableDoc.query.filter_by(category=category).first()
            if old_doc:
                old_file_path = os.path.join(save_path, old_doc.filename)
                if os.path.exists(old_file_path): os.remove(old_file_path)
                db.session.delete(old_doc)
                db.session.flush()
            
            file.save(os.path.join(save_path, filename))
            new_doc = DownloadableDoc(title=title, category=category, filename=filename)
            db.session.add(new_doc)
            db.session.commit()
            flash("File updated successfully!", "success")
            return redirect(url_for('admin_docs'))
            
    all_docs = DownloadableDoc.query.all()
    return render_template("admin/documents.html", all_docs=all_docs)

# 2. Delete Route (Dedicated)
@app.route("/admin/delete_doc/<int:id>", methods=['POST'])
@login_required
def delete_doc(id):
    doc = DownloadableDoc.query.get_or_404(id)
    save_path = os.path.join(app.root_path, 'static', 'uploads', 'docs')
    file_path = os.path.join(save_path, doc.filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    db.session.delete(doc)
    db.session.commit()
    flash("File deleted successfully!", "success")
    return redirect(url_for('admin_docs'))






# ========================= APP RUNNER =========================





import os
from sqlalchemy import text, inspect

# --- Database Setup Helper ---
def setup_database():
    with app.app_context():

        # create tables first
        db.create_all()

        engine = db.engine
        inspector = inspect(engine)

        def table_exists(table_name):
            return inspector.has_table(table_name)

        def column_exists(table_name, column_name):
            if not table_exists(table_name):
                return False
            return column_name in [c["name"] for c in inspector.get_columns(table_name)]

        # -----------------------------
        # SAFE COLUMN UPDATES LIST
        # -----------------------------
        updates = [
            ("inquiry", "address", "VARCHAR(255)"),
            ("video", "video_type", "VARCHAR(50)"),
            ("video", "embed_code", "TEXT"),
        ]

        # -----------------------------
        # APPLY MIGRATIONS SAFELY
        # -----------------------------
        with engine.begin() as conn:
            for table, col, col_type in updates:

                if table_exists(table) and not column_exists(table, col):
                    try:
                        conn.execute(
                            text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                        )
                        print(f"✅ Added column {col} to {table}")

                    except Exception as e:
                        print(f"⚠️ Failed adding {col} to {table}: {e}")

        print("✅ Database verification complete (safe mode)")


# -----------------------------
# CALL ON START (IMPORTANT)
# -----------------------------
setup_database()


# -----------------------------
# RUNNER (Render safe)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)    app.run(host="0.0.0.0", port=port, debug=False)