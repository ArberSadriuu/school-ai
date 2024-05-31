from flask import jsonify, request
import requests
from db import contests, insert, schools
from datetime import datetime


def createContest(id):
  data = request.get_json()
  school = schools(id)
  if school:
    published = data['published' if 'published' in data else False]
    if 'activeuntil' not in data:
      return jsonify({"message":
                      "Konkursi qe po kerkoni nuk eshte aktiv"}), 400

    current_time = datetime.now()
    if current_time <= datetime.strptime(data['activeUntil'],
                                         '%Y-%m-%d %H:%M:%S'):
      insert(
          'contests', {
              'title': data['title'],
              'description': data['description'],
              'school_id': id,
              'aiorders': data['aiOrders'],
              'activeuntil': data['activeuntil'],
              'published': data['published'],
              'nrstudents': data['nrStudents']
          })
    else:
      return jsonify({"message": "Konkursi nuk eshte aktiv"}), 400
  else:
    return jsonify({"message": "Shkolla nuk eshte regjistruar"}), 404


def apply(id):
  data = request.get_json()
  contest = contests(id=id)  # Replace with the actual base URL of your API
  full_url = "https://f5de9278-e3d3-487d-9c8b-6d1d4bdc4725-00-h4scbmu0npph.kirk.replit.dev/message"

  # Make the POST request with the JSON payload
  response = requests.post(full_url,
                           json={
                               "message": data['description'],
                               "aiOrders": contest[0]['aiorders'],
                           })

  def calculateResponse(response):
    if (response['message'] == "True"):
      return True
    else:
      return False

  insert(
      'students', {
          'name': data['name'],
          'description': data['description'],
          'phone': data['phone'],
          'contest_id': id,
          'school_id': data['school_id'],
          'classified': calculateResponse(response.json()),
      })

  return jsonify({"message": "You are accepted"})
