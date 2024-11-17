from flask import Flask, request, jsonify
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://doc_pat:27lodima@192.168.1.111:5433/doc_pat_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class SymptomCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.String(10), nullable=False)
    condition = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/symptom_checks', methods=['GET'])
def get_symptom_checks():
    patient_id = request.args.get('patient_id')
    doctor_id = request.args.get('doctor_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = SymptomCheck.query

    if patient_id:
        query = query.filter(SymptomCheck.patient_id == patient_id)
    if doctor_id:
        query = query.filter(SymptomCheck.doctor_id == doctor_id)
    if start_date:
        query = query.filter(SymptomCheck.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(SymptomCheck.created_at <= datetime.fromisoformat(end_date))

    results = query.all()
    return jsonify([{
        'id': sc.id,
        'patient_id': sc.patient_id,
        'doctor_id': sc.doctor_id,
        'temperature': sc.temperature,
        'pressure': sc.pressure,
        'condition': sc.condition,
        'created_at': sc.created_at.isoformat()
    } for sc in results])


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
