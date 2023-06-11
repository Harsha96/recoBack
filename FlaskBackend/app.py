from flask import Flask, request, jsonify
import pickle
import pandas as pd
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from pymongo import MongoClient
from flask_cors import CORS
import numpy as np
# from sklearn.calibration import CalibratedClassifierCV
# from sklearn.preprocessing import LabelEncoder
# from sklearn.preprocessing import KBinsDiscretizer

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY4MTM5MDc2NywiaWF0IjoxNjgxMzkwNzY3fQ.ySbTok2__5tOXTzP2I9AE8pAqDOgapotbsPX7r-I-ts'

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Set up MongoDB connection
client = MongoClient('mongodb+srv://admin:NUXCf9TigT0nCLzk@cluster0.cpmky.gcp.mongodb.net/reco?retryWrites=true&w=majority')
db = client['reco']
users_collection = db['users']
revoked_tokens_collection=db['revoked_tokens_collection']
from bson import ObjectId
import json

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)
app.json_encoder = CustomJSONEncoder

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    # Get the data from the request
    data = request.get_json()

    # Check if the user already exists
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists'}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Insert the new user into the database
    user = {
        'email': data['email'],
        'password': hashed_password,
        'firstName': data.get('firstName', ''),
        'lastName': data.get('lastName', ''),
        'city': data.get('city', ''),
        'province': data.get('province', ''),
        'registrationNumber': data.get('registrationNumber', ''),
        'religious': data.get('religious', ''),
        'gender': data.get('gender', ''),
        'working': data.get('working', False),
        'alResults': data.get('alResults', {}),
        'olResults': data.get('olResults', {}),
        'userRole': data['userRole'],
        'married':data.get('married',False),
        'birthday': data.get('birthday', ''),
        'stream':data.get('stream',''),
        'passedList': data.get('passedList', []),
        'eligibleOnly': data.get('eligibleOnly', []),
        'pendingEligible': data.get('pendingEligible', [])
    }
    users_collection.insert_one(user)

    return jsonify({'message': 'User created successfully'}), 201

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    # Get the data from the request
    data = request.get_json()

    # Check if the user exists
    user = users_collection.find_one({'email': data['email']})
    if not user:
        return jsonify({'message': 'Invalid email or password'}), 401

    # Check the password
    if not bcrypt.check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Create access token
    access_token = create_access_token(identity=user['email'])

    return jsonify({'access_token': access_token}), 200

# Protected endpoint
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Get the current user identity
    current_user = get_jwt_identity()

    return jsonify({'message': 'Sorry, {}! This is a protected endpoint.'.format(current_user)}), 200

# Load the trained model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
# Get the unique degree labels from the dataset
unique_labels = ["Bachelor of Technology (BTech) Honours in Agriculture and Plantation Engineering",
"Bachelor of Industrial Studies Honours - Agriculture",
"Bachelor of Software Engineering Honours"
"Bachelor of Technology - Electronic and Communication Engineering",
"Bachelor of Technology - Mechanical Engineering",
"Bachelor of Technology - Mechatronics Engineering",
"Bachelor of Technology - Electrical Engineering",
"Bachelor of Technology - Computer Engineering",
"Bachelor of Technology - Civil Engineering",
"Bachelor of Technology Honours in Engineering – Textile & Clothing",
"Bachelor of Industrial Studies Honours – Textile Manufacture Specialization",
"Bachelor of Industrial Studies Honours – Fashion Design and Product Development",
"Bachelor of Industrial Studies Honours – Apparel Production and Management"]


# load the svm
with open('svm_models.pkl', 'rb') as f:
    models = pickle.load(f)
    # load data
df = pd.read_csv('course.csv')
subject_names = df.columns[2:] 


@app.route('/user/<string:email>', methods=['GET'])
@jwt_required()
def get_user(email):
    # Check if the requesting user is an admin or requesting their own details
    current_user = get_jwt_identity()
    user = users_collection.find_one({'email': email}, {'_id': False, 'password': False})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if current_user == email or current_user == 'admin':
        return jsonify({'user': user}), 200
    else:
        return jsonify({'message': 'Unauthorized'}), 401
    
@app.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    # Get the data from the request
    data = request.get_json()

    # Convert the data to a DataFrame
    X = pd.DataFrame.from_dict(data, orient='index').T

    # Make sure the input DataFrame has the same columns as the training data
    X = X[['educational_factor', 'social_factor']]

    # Make predictions using the loaded model
    probabilities = model.predict_proba(X)[0]

    # Get the unique degree labels
    unique_labels = model.classes_

    # Find the index of the degree with the highest probability
    max_prob_index = np.argmax(probabilities)

    # Get the most suitable degree and its corresponding probability
    most_suitable_degree = unique_labels[max_prob_index]
    probability = probabilities[max_prob_index]

    # Return the most suitable degree and its probability as a JSON response
    return jsonify({'Degree': most_suitable_degree, 
                    # 'Probability': probability
                    })



# Logout endpoint
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    try:
        revoked_tokens_collection.insert_one({'jti': jti})
    except:
        return jsonify({'message': 'An error occurred while revoking the token'}), 500
    return jsonify({'message': 'Token revoked'}), 200

@app.route('/course-recommend', methods=['POST'])
@jwt_required()
def course_recommendation():
    data = request.get_json()  # Get the input data from the request

    # Prepare input data for prediction
    social_factor = data['social_factor']
    educational_factor = data['educational_factor']
    input_data = [[social_factor, educational_factor]]

    # Predict probabilities for each subject's success
    predictions = []
    for i, model in enumerate(models):
        subject_name = subject_names[i]
        probability = model.predict_proba(input_data)[:, 1][0]  # Predict for the current subject
        predictions.append({
            'probability': probability,
            'subject': subject_name
        })
        
    # Sort the predictions in descending order based on probability
    sorted_predictions = sorted(predictions, key=lambda x: x['probability'], reverse=True)
    return {'recommendations': sorted_predictions}

courses_collection = db['courses']  # Replace with your collection name

@app.route('/course', methods=['POST'])
@jwt_required()
def create_course():
    # Get the course details from the request
    data = request.get_json()
    course_code = data['courseCode']

    # Check if the course already exists
    if courses_collection.find_one({'courseCode': course_code}):
        return jsonify({'message': 'Course already exists'}), 400

    course_name = data['courseName']
    eligibility_criteria = data['EligibilityCriteria']
    academic_coordinator_name = data['AcademicCoordinator']['name']
    academic_coordinator_email = data['AcademicCoordinator']['email']
    academic_coordinator_contact = data['AcademicCoordinator']['contact']
    course_coordinator_name = data['CourseCoordinator']['name']
    course_coordinator_email = data['CourseCoordinator']['email']
    course_coordinator_contact = data['CourseCoordinator']['contact']
    prerequisites = data['Prerequisites']

    # Create the course document
    course = {
        'courseCode': course_code,
        'courseName': course_name,
        'EligibilityCriteria': eligibility_criteria,
        'AcademicCoordinator': {
            'name': academic_coordinator_name,
            'email': academic_coordinator_email,
            'contact':academic_coordinator_contact,
        },
        'CourseCoordinator': {
            'name': course_coordinator_name,
            'email': course_coordinator_email,
            'contact':course_coordinator_contact,
        },
        'Prerequisites':prerequisites
    }

    # Insert the course document into the database
    courses_collection.insert_one(course)

    # Return a response indicating the course was created successfully
    return jsonify({'message': 'Course created successfully'})

@app.route('/course/<course_code>', methods=['GET'])
@jwt_required()
def get_course(course_code):
    # Find the course by course code in the database
    course = courses_collection.find_one({'courseCode': course_code})

    if course:
        # Course found, return the course details
        return jsonify(course)
    else:
        # Course not found, return an error message
        return jsonify({'message': 'Course not found'}), 404

@app.route('/add-courses/<email>', methods=['POST'])
@jwt_required()
def update_user(email):
    # Get the data from the request
    data = request.get_json()

    # Find the user by email
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Extract the course code from the data
    course_code = data.get('courseCode')

    # Check if the course code already exists in any of the arrays
    if course_code in user['passedList'] or course_code in user['eligibleOnly'] or course_code in user['pendingEligible']:
        return jsonify({'message': 'Course code already exists in user\'s arrays'}), 400

    # Update the user details based on the form data
    if data.get('pass'):
        user['passedList'].append(course_code)

    if data.get('eligibility'):
        user['eligibleOnly'].append(course_code)

    if data.get('pending'):
        user['pendingEligible'].append(course_code)

    # Update the user in the database
    users_collection.update_one({'email': email}, {'$set': user})

    return jsonify({'message': 'User updated successfully'}), 200

@app.route('/delete-courses/<email>', methods=['POST'])
def delete_user_code(email):
    # Get the data from the request
    data = request.get_json()

    # Find the user by email
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Update the user details based on the form data
    if data.get('pass'):
        course_code = data.get('courseCode')
        if course_code in user['passedList']:
            user['passedList'].remove(course_code)

    if data.get('eligibility'):
        course_code = data.get('courseCode')
        if course_code in user['eligibleOnly']:
            user['eligibleOnly'].remove(course_code)

    if data.get('pending'):
        course_code = data.get('courseCode')
        if course_code in user['pendingEligible']:
            user['pendingEligible'].remove(course_code)

    # Update the user in the database
    users_collection.update_one({'email': email}, {'$set': user})

    return jsonify({'message': 'User updated successfully'}), 200
if __name__ == '__main__':
    app.run(debug=True)