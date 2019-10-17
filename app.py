import os

from bson.objectid import ObjectId

from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient

client = MongoClient()
db = client.MedImaging
medfiles = db.medfiles
patients = db.patients

app = Flask(__name__)


@app.route('/')
def index():
    read_patients = patients.find()

    return render_template('index.html', patients=read_patients)

@app.route('/patients/new')
def patient_new():

    return render_template('patient_new.html', patient={}, title="New Patient")

@app.route('/patients', methods=['POST'])
def patient_submit():
    patient = {
        'name': request.form.get('name'),
        'dob': request.form.get('dob'),
        'sex': request.form.get('sex')
       
    }
    print(patient)
    patient_id = patients.insert_one(patient).inserted_id
    return redirect(url_for('patient_show', patient_id=patient_id))

@app.route('/patients/<patient_id>')
def patient_show(patient_id):
    patient = patients.find_one({'_id': ObjectId(patient_id)})
    patient_files = medfiles.find({'patient_id': ObjectId(patient_id)})

    return render_template('patient_show.html', patient=patient, patient_files=patient_files)

@app.route('/patients/<patient_id>/edit')
def patient_edit(patient_id):
    patient = patients.find_one({'_id': ObjectId(patient_id)})
    return render_template('patient_edit.html', patient=patient, title='Edit Patient')

@app.route('/patients/<patient_id>', methods=['POST'])
def patient_update(patient_id):
    updated_patient = {
        'name': request.form.get('name'),
        'dob': request.form.get('dob'),
        'sex': request.form.get('sex')
    }
    patients.update_one(
        {'_id': ObjectId(patient_id)},
        {'$set': updated_patient}
    )
    return redirect(url_for('patient_show', patient_id=patient_id))

@app.route('/patients/<patient_id>/delete', methods=['POST'])
def patient_delete(patient_id):
    patients.delete_one({'_id': ObjectId(patient_id)})

    return redirect(url_for('index'))

@app.route('/patients/files', methods=['POST'])
def files_new():
    medfile = {
        'type': request.form.get('type'),
        'name': request.form.get('content'),
        'patient_id': ObjectId(request.form.get('patient_id'))
    }   
    print(medfile)
    medfile_id = medfiles.insert_one(medfile).inserted_id
    return redirect(url_for('patient_show', patient_id=request.form.get('patient_id')))
