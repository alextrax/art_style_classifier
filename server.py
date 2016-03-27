#!/usr/bin/env python2.7

import os
import errno
from flask import Flask, g, request, render_template
from sqlalchemy import *


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
img_dir = "/Volumes/Alex/Columiba_course/Visual_DB/Project/database/wikiart/images/"

app = Flask(__name__, template_folder=tmpl_dir)

app.secret_key = os.urandom(24)


DATABASEURI = "postgresql://localhost/artdb"
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/show_img_byID')
def show_img_byID():
  img_id = request.args.get("img_id")
  if img_id != None:
    cursor = g.conn.execute("SELECT * FROM imgs WHERE id = %s", img_id)
    img_info = cursor.fetchone() 
    if img_info != None:
      url = "/static/img/" + img_info['name']
      return render_template("show_image.html", name = img_info['name'],  url = url, style = img_info['style'])
    else:
      return "img does not exist" 

if __name__ == "__main__":
  import click
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=7788, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """
    try:
      os.symlink(img_dir, static_dir + "/img")
    except OSError, e:
      if e.errno == errno.EEXIST:
        os.remove(static_dir + "/img")
        os.symlink(img_dir, static_dir + "/img")


    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
    
  run()
