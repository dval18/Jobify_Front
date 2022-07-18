from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy

import pandas as pd
import random
import requests
import json
import pprint
import sqlalchemy as db
import pdb
from sqlalchemy.types import String

app = Flask(__name__)

