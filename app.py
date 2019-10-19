import os

from bson.objectid import ObjectId

from flask import Flask, redirect, render_template, request, url_for, send_from_directory, flash
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo

'''Sets the variables for URI and Uploads'''
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'dcm'])
UPLOADS_FOLDER = '/Users/omarsagoo/dev/courses/intensive/med-imaging/static/files/uploads'
URI = 'mongodb://localhost:27017/MedImaging'

''' Variables for app configuration and creating the DB'''
app = Flask(__name__)
app.config["UPLOADS_FOLDER"] = UPLOADS_FOLDER
app.config["ALLOWED_EXT"] = ALLOWED_EXTENSIONS
app.config['MONGO_URI'] = URI
mongo = PyMongo(app, URI)
host = os.environ.get('MONGODB_URI', URI)
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
medfiles = db.medfiles
patients = db.patients

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    '''creates the route for the uploaded files to be displayed '''
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/')
def index():
    '''Main homepage displays all the patients'''
    read_patients = patients.find()

    return render_template('index.html', patients=read_patients)

@app.route('/patients/new')
def patient_new():
    '''returns the teemplate for creating a new patient '''
    return render_template('patient_new.html', patient={}, title="New Patient")

@app.route('/patients', methods=['POST'])
def patient_submit():
    '''submits the patient into the DB and redirects back to patient show to display the information'''
    patient = {
        'name': request.form.get('name'),
        'dob': request.form.get('dob'),
        'sex': request.form.get('sex')
       
    }
    # print(patient)
    patient_id = patients.insert_one(patient).inserted_id
    return redirect(url_for('patient_show', patient_id=patient_id))

@app.route('/patients/<patient_id>')
def patient_show(patient_id):
    ''' shows the patients on the page '''
    patient = patients.find_one({'_id': ObjectId(patient_id)})
    patient_files = medfiles.find({'patient_id': ObjectId(patient_id)})

    return render_template('patient_show.html', patient=patient, patient_files=patient_files)

@app.route('/patients/<patient_id>/edit')
def patient_edit(patient_id):
    '''allows editing of the database files of the patients'''
    patient = patients.find_one({'_id': ObjectId(patient_id)})
    return render_template('patient_edit.html', patient=patient, title='Edit Patient')

@app.route('/patients/<patient_id>', methods=['POST'])
def patient_update(patient_id):
    '''updates the patients in the database with patient_edit'''
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
    '''deletes a patient from the database'''
    patients.delete_one({'_id': ObjectId(patient_id)})

    return redirect(url_for('index'))

def allowed_file(filename):
    ''' makes sure that files with the allowed extensions can be inputed only '''
    if not '.' in filename:
        return False
    
    ext = filename.rsplit(".",1)[1]

    if ext.lower() in app.config["ALLOWED_EXT"]:
        return True
    else:
        return False

@app.route('/patients/files', methods=['POST'])
def files_new():
    '''uploads the files into the uploads file, and makes sure the files are secure, have a name and are allowed '''
    if request.method == 'POST':
        if request.files:
            med_file = request.files['file']
            mongo.save_file(med_file.filename, med_file)
            if med_file.filename == "":
                print('image must have file name')
                return redirect(url_for('patient_show', patient_id=ObjectId(request.form.get('patient_id'))))

            if not allowed_file(med_file.filename):
                print("That file ext is not allowed")
                return redirect(url_for('patient_show', patient_id=ObjectId(request.form.get('patient_id'))))
            else:
                filename = secure_filename(med_file.filename)
                med_file.save(os.path.join(app.config["UPLOADS_FOLDER"], filename))

            print('image saved')
            ''' creates the medfile database structure '''
            medfile = {
                'type': request.form.get('type'),
                'name': request.form.get('name'),
                'filesize': int(request.cookies['filesize'])/1000,
                'filename': med_file.filename,
                'patient_id': ObjectId(request.form.get('patient_id'))
            }   
            medfile_id = medfiles.insert_one(medfile).inserted_id
            return redirect(url_for('patient_show', patient_id=ObjectId(request.form.get('patient_id'))))



@app.route('/patients/files/<medfile_id>', methods=['POST'])
def files_delete(medfile_id):
    ''' deletes a file from the database '''
    medfile = medfiles.find_one({'_id': ObjectId(medfile_id)})
    medfiles.delete_one({'_id': ObjectId(medfile_id)})
    return redirect(url_for('patient_show', patient_id=medfile.get('patient_id')))

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))