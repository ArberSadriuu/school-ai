# Importimi
from flask import Flask, jsonify, request, Response, make_response
import os
from supabase import create_client, Client
from db import insert, schools, contests, students
from functions import apply, createContest
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import openai

openai.api_key = os.environ['OPENAI_API_KEY']
url: str = os.environ['SUPABASE_URL']
key: str = os.environ['SUPABASE_KEY']
supabase: Client = create_client(url, key)

# Flask app
app = Flask('app')
CORS(app)

app.config['SECRET_KEY'] = 'jHbIYEd36g'


@app.route('/')
def hello_world():
  return "Server is running"


@app.route('/register', methods=['POST'])
def register():
  data = request.get_json()
  school = schools(email=data['email'])
  hashed_password = generate_password_hash(data['password'])
  data['password'] = hashed_password
  if (school):
    return Response("School already exists", status=400)
  else:
    insert('schools', data)
    return Response("School registered", status=200)


# Endpoint per Login
@app.route('/login', methods=['POST'])
def login():
  data = request.get_json()
  school = schools(email=data['email'])
  if not school:
    return Response("School not found", status=400)
  elif not check_password_hash(school[0]['password'], data['password']):
    return Response("Invalid password", status=400)
  else:
    token = str((school[0]['id']))
    response = make_response(
        jsonify({
            "message": "Login successful",
            "token": token
        }), 200)
    return response


@app.route('/schools')
def get_schools():
  response = schools()
  print(f"response: {response}")
  data = response
  # Serialize the data into JSON
  serialized_data = jsonify(data)
  return serialized_data


@app.route('/school/<string:id>', methods=['GET'])
def get_school(id):
  response = schools(id)
  print(f"response: {response}")
  data = response
  # Serialize the data into JSON
  serialized_data = jsonify(data[0])
  return serialized_data


@app.route('/contests/<string:id>', methods=['GET'])
def get_contests(id):
  response = contests(school=id)
  data = response
  # Serialize the data into JSON
  serialized_data = jsonify(data)
  return serialized_data


@app.route('/contest/<string:id>', methods=['POST'])
def add_contest(id) -> Response:
  createContest(id)
  return Response(status=200)


@app.route('/contest/<string:id>', methods=['GET'])
def get_contest(id):
  response = contests(id=id)
  data = response
  # Serialize the data into JSON
  serialized_data = jsonify(data[0])
  return serialized_data


@app.route('/students/<string:id>', methods=['GET'])
def get_students(id):
  response = students(school=id)
  # Serialize the data into JSON
  serialized_data = jsonify(response)
  return serialized_data


@app.route('/students/contest/<string:id>', methods=['GET'])
def get_contest_students(id):
  response = students(contest=id)

  serialized_data = jsonify(response)
  return serialized_data

@app.route('/contest/published/<string:id>', methods=['PUT'])
def update_contest_published(id):
  contest = contests(id)
  if contest:
    data = request.get_json()
    published = data['published']
    supabase.table('contests').update(published).eq('id', id).execute()

    return jsonify({"message": f"Konkursi me id:{id} u publikua me sukses", "contest": contest})
  else:
    return jsonify({"message": f"Nuk ka konkurs me kete id"}), 400


@app.route('/apply/<string:id>', methods=['POST'])
def add_student(id) -> Response:
  apply(id)
  return Response(status=200)


@app.route('/accepted/<string:id>', methods=['GET'])
def get_accepted_students(id) -> Response:
  response = supabase.table('students').select("*").eq('school_id', id).eq(
      'classified', True).execute().data
  data = response
  # Serialize the data into JSON
  serialized_data = jsonify(data)
  return serialized_data


# Pranimi i mesazhit prej json dhe dergimi i mesazhit ne chatgpt permes openai api dhe pasi te behet requesti te na i kthej nje pergjigjje
@app.route('/message', methods=['POST'])
def message() -> Response:
  data = request.get_json()
  message = data['message']
  aiOrders = data['aiOrders']

  response = openai.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{
          "role":
          "system",
          "content":
          f"Classify the upcoming student based on these very strict condition, take care and do not make mistakes. Also give me only True or false: + {aiOrders}"
      }, {
          "role": "user",
          "content": message
      }],
      temperature=0,
      max_tokens=1000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0)

  if (response):
    return jsonify({"message": response.choices[0].message.content})

  else:
    return Response("Error", status=400)


@app.route('/analyze-image', methods=['POST'])
def analyze_image() -> Response:
  data = request.get_json()
  image = data['image']
  response = openai.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[{
          "role":
          "user",
          "content": [
              {
                  "type":
                  "text",
                  "text":
                  "Ne kete foto jane nota te nje nxenesit, andaj llogarite mesataren e te gjitha notave the ma jep ate vlere. Sigurohu qe llogaritjen ta besh mire gjithmone dhe kur ta besh pershkrimin beje sikur te jesh duke folur ne veten e pare p.sh 'Notat e mia jane...', 'Mesatarja ime eshte...' dhe pergjigja te mos jete shume e gjate. Thjeshte teper pak pershkrim i notave dhe mesatarja e tyre."
              },
              {
                  "type": "image_url",
                  "image_url": {
                      "url": image,
                  },
              },
          ],
      }],
      max_tokens=300,
  )
  return Response(response.choices[0].message.content)


app.run(host='0.0.0.0', port=8080)
