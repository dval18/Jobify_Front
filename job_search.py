# start with the imports
from sqlalchemy import exc
import pandas as pd
import random
import requests
import json
import pprint
import pdb
import sqlite3
from functools import wraps
from sqlalchemy.types import String
from flask import Flask, request, render_template, url_for, flash, redirect, g, jsonify, session
from flask_session import Session
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy

DATABASE ='./jobify.db'


app = Flask(__name__)
proxied = FlaskBehindProxy(app)

app.config['SECRET_KEY'] = 'f8ab5567ef84a9ee5c1e3d86bb8b9ef9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobify.db'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy(app)
Session(app)

# '''# interchange use of API Keys to limit searches to not get 100
API_KEYS = ('e21193f2b2ee7a0a7042c7a414822b20b10c84609c42a408732401d8b62ddc06',
            '9e8e77e8075bf5f1bfbbef8848ba3b735d1cf01e0490877307eded9945e41777',
            'c385df59163477b88fa13574e0bb8886c32b687a8eb0b8dded75b959def7262b')

key_index = random.randint(0, 2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            flash("Error: Need to be logged in to access.", 'error')
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

class User(db.Model):
  try:
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(20), unique=True, nullable=False)
        password = db.Column(db.String(60), nullable=False)
  except Exception as e:
        print('hi')
  def __repr__(self):
    return f"User('{self.username}', '{self.id}')"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def valid_login(username, password):
    user = query_db('select * from User where username = ? and password = ?', [username, password], one=True)
    if user is None:
        return False
    else:
        return True


def log_the_user_in(username):
    session['username'] = username
    return render_template(('logged-in-home.html'), username=username)

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.Integer, db.ForeignKey('User.username'))
    job_title=db.Column(db.String())
    company_name=db.Column(db.String())
    location=db.Column(db.String())
    description=db.Column(db.String())

    def __repr__(self):
        return f"Job:('{self.job_title}: {self.company_name}')"

@app.route("/saved_jobs", methods=('GET', 'POST'))
def save_job():
    # print(request_data.get('job_title'))
    #get value from checkbox?
    if request.method == 'POST':
        job_title = request.json.get('job_title')
        company_name = request.json.get('company_name')
        job_location = request.json.get('location')
        job_description = request.json.get('description')
        saved_job = SavedJob(job_title=job_title,company_name=company_name, location=job_location, description=job_description)
        db.session.add(saved_job)
        db.session.commit()
        return jsonify(status="success")
        return render_template(('saved_jobs.html'), job_title=job_title, company_name=company_name, job_location=job_location, job_description=job_description)
        

    # results = {'processed': 'true'}
    # print(jsonify(results))
 
#  results = {'processed': 'true'}
#  return jsonify(results)
#         saved_job = SavedJob(job_title=job_title,company_name=company_name, location=location, description=description)
#         db.session.add(saved_job)
#         db.session.commit()



@app.route("/")
def homepage():
    return render_template('home.html')

@app.route("/job_search", methods=('GET', 'POST'))
@login_required
def job_search():
    if request.method == 'POST':
        job_fields = request.form['fields']
        job_location = request.form['location']
        #parse info from form into api to get request
        r = requests.get(f'https://serpapi.com/search.json?engine=google_jobs&q={job_fields}&location={job_location}&api_key={API_KEYS[key_index]}')
        data = r.json()['jobs_results']
        return render_template('jobs_list.html', data = data)
    return render_template('job_search.html')

@app.route("/jobs_list")
@login_required
def jobs_list():
    return render_template('jobs_list.html')


@app.route("/about")
@login_required
def about_page():
    return render_template('about.html')

@app.route("/saved-jobs")
def saved_jobs_page():
    jobs_saved = SavedJob.query.all()
    return render_template('saved-jobs.html', jobs = jobs_saved)

@app.route("/contact")
def contact_page():
    return render_template('contact.html')

@app.route('/register', methods=('GET', 'POST'))
def register_form():
    form = RegistrationForm()
    if form.validate_on_submit() and request.method == 'POST':
        try:
            user = User(username=form.username.data, password=form.password.data)
            # engine = db.create_engine('sqlite:///jobify.db', {})
            # id = engine.execute("INSERT INTO user (username, password) VALUES(?, ?)", form.username.data, form.password.data)
            # print(id)
            db.session.add(user)
            db.session.commit()
            session['username'] = user.username
        except exc.SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            if 'UNIQUE' in error:
                flash('Unique Error: Username already taken. Please Try again with a Different Username', 'error')
            else:
                flash('Error: Try Again', 'error')
            return redirect(url_for('register_form'))
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('homepage'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    session.clear()
    print(session)
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = ' '
            flash(error,"error")
    return render_template('login.html', error=error)




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

'''# interchange use of API Keys to limit searches to not get 100
API_KEYS = ('e21193f2b2ee7a0a7042c7a414822b20b10c84609c42a408732401d8b62ddc06',
            '9e8e77e8075bf5f1bfbbef8848ba3b735d1cf01e0490877307eded9945e41777')

key_index = random.randint(0, 1)


def print_func(query):
    df = pd.DataFrame(query)
    df.columns = ['user_id', 'title', 'company_name', 'location', 'via', 'description', 'job_id', 'detected_extensions.posted_at', 'detected_extensions.schedule_type']
    pprint.pprint(df)

def print_links(id_list):
        list_data = []
        for id in id_list:
            request = requests.get(f'https://serpapi.com/search.json?\
engine=google_jobs_listing&q={id}&api_key={API_KEYS[key_index]}')
            link_data = request.json()["apply_options"]
            list_data.append(link_data)
        for i in range(len(list_data)):
            print(f'job {i + 1}:')
            for j in range(len(list_data[i])):
                for key, value in list_data[i][j].items():
                    if key == 'link' and j <= 3:
                        print(f'Application Link {j}: {list_data[i][j][key]}')

def user_check(user_name):
    if user_name == None:
        return False
    names = user_name.split('_')
    if len(names) != 2:
        print("Invalid firstname_lastname")
        return False
    for name in names:
        for letter in name:
            if not ('a' <= letter <= 'z') and not ('A' <= letter <= 'Z'):
                print("Invalid firstname_lastname")
                return False
    return True

def enter_into_database(data, user):
    data_table = pd.json_normalize(data)
    data_table.insert(0, 'user_id', user)
    # print(data_table)
    engine = db.create_engine('sqlite:///job-search-results.db')
    data_table.to_sql('jobs', con=engine, if_exists='append', index=False)#need to fix
    query = engine.execute(f"SELECT * FROM jobs WHERE user_id='{user}'").fetchall()
    print_func(query)
    return engine

def program_driver(user_name):
    engine = db.create_engine('sqlite:///job-search-results.db')
    num_user = engine.execute(f"SELECT COUNT(user_id) FROM jobs WHERE user_id='{user_name}';").fetchone()[0]
    if num_user > 0:
        print(f"Welcome back, {user_name.replace('_', ' ').title()}!")
        query = engine.execute(f"SELECT * FROM jobs WHERE user_id='{user_name}';")
        id_list = engine.execute(f"SELECT job_id FROM jobs WHERE user_id='{user_name}';").fetchall()
        id_list = [id[0] for id in id_list]
        print_func(query)
        print_links(id_list)
        answer = input("If you would like to research different jobs, press 'y' and hit enter. Otherwise, hit enter: ").lower().strip()
        if answer == 'y':
            search_api()
    else:
        search_api()


def search_api():
    job_fields = input("Enter comma-separated fields \
in which you would like to search for jobs: ").strip()
    location = input("(OPTIONAL) Enter a location for jobs,\
else hit enter: ").strip()

    
    # make GET request and convert to json data containing job results
    r = requests.get(f'https://serpapi.com/search.json?engine=google_jobs&q={job_fields}&location={location}&api_key={API_KEYS[key_index]}')
    data = r.json()['jobs_results']
    for job in data:
        job.pop('extensions', None)
        job.pop('thumbnail', None)
    pprint.pprint(data[:5])

    job_nums = input("type the number of the job you are interested in. \
(Number meaning what place in the order shown) If you are interested \
in multiple, seperate numbers with a ',': ")
    nums = job_nums.split(',')
    id_list = []
    dict_list = []
    for num in nums:
        id_list.append(data[int(num) - 1]['job_id'])
        dict_list.append(data[int(num) - 1])   
    enter_into_database(dict_list, user_name)
    print_links(id_list) 

if __name__ == '__main__':
    user_name = None
    while not user_check(user_name):
        user_name = input("Please type your firstname_lastname: ").lower().strip()
    program_driver(user_name)'''
