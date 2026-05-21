from app import db


class BugReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_text = db.Column(db.Text, nullable=False)
