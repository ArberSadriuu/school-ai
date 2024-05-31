import os
from supabase import create_client, Client

url: str = os.environ['SUPABASE_URL']
key: str = os.environ['SUPABASE_KEY']
supabase: Client = create_client(url, key)


def insert(table, data, id=None):
  supabase.table(table).insert(data).execute()
  if (id):
    supabase.table(table).update({"id": id}).execute()


def schools(id=None, email=None):
  response = None
  if (id):
    response = supabase.table('schools').select("*").eq('id',
                                                        id).execute().data
  elif (email):
    response = supabase.table('schools').select("*").eq('email',
                                                        email).execute().data
  else:
    response = supabase.table('schools').select("*").execute().data
  return response


def contests(school=None, id=None):
  response = None
  if (id):
    response = supabase.table('contests').select("*").eq('id',
                                                         id).execute().data
  elif (school):
    response = supabase.table('contests').select("*").eq('school_id',
                                                         school).execute().data
  elif (school and id):
    response = supabase.table('contests').select("*").eq(
        'school_id', school).eq('id', id).execute().data

  else:
    response = supabase.table('contests').select("*").execute().data
  return response


def students(contest=None, school=None, id=None):
  response = None
  if (id):
    response = supabase.table('students').select("*").eq('id',
                                                         id).execute().data
  elif (school):
    response = supabase.table('students').select("*").eq('school_id',
                                                         school).execute().data
  elif (contest):
    response = supabase.table('students').select("*").eq(
        'contest_id', contest).execute().data
  elif (school and id):
    response = supabase.table('students').select("*").eq(
        'school_id', school).eq('id', id).execute().data

  else:
    response = supabase.table('students').select("*").execute().data
  return response
