from app import app, db
from sqlalchemy import text

with app.app_context():
    columns_to_add = [
        "first_term_total",
        "half_yearly_total",
        "grand_total"
    ]
    
    for col in columns_to_add:
        try:
            # Har column ko alag se execute aur commit karein
            db.session.execute(text(f"ALTER TABLE results ADD COLUMN {col} FLOAT DEFAULT 0"))
            db.session.commit()
            print(f"Successfully added column: {col}")
        except Exception as e:
            db.session.rollback() # Agar error aaye toh transaction reset karein
            print(f"Could not add {col} (might already exist): {e}")

    print("Database check completed!")