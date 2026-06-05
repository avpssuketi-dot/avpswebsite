from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Columns add karne ki koshish
        db.session.execute(text("ALTER TABLE results ADD COLUMN first_term_total FLOAT DEFAULT 0"))
        db.session.execute(text("ALTER TABLE results ADD COLUMN half_yearly_total FLOAT DEFAULT 0"))
        db.session.execute(text("ALTER TABLE results ADD COLUMN grand_total FLOAT DEFAULT 0"))
        db.session.commit()
        print("Database successfully updated with new columns!")
    except Exception as e:
        print("Database pehle se updated hai ya error aaya:", e)