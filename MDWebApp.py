from flask import Flask, render_template, redirect, send_from_directory, request, url_for, abort, flash
from time import ctime
from datetime import datetime
from flask_basicauth import BasicAuth
import markdown
import os
import shutil

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
app.config['BASIC_AUTH_USERNAME'] = 'user'
app.config['BASIC_AUTH_PASSWORD'] = 'start!123'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
basic_auth = BasicAuth(app)
indexmd = os.path.join(app.root_path,'md','index.md')
context_routes_folder = os.path.join(app.root_path,'md')
context_routes = []

@app.errorhandler(404)
def custom404(e):
	return redirect('/')

@app.route("/favicon.ico")
def favicon():
	return send_from_directory(os.path.join(app.root_path,'static','img'), 'favicon.ico', mimetype = 'image/vnd.microsoft.icon')

@app.route("/")
def index():
	if os.path.isfile(indexmd):
		with open(indexmd) as mdfile:
			MDContent = markdown.markdown(mdfile.read(), extensions=['fenced_code','codehilite'])
	else:
		MDContent = None

	return render_template('index.html', MDContent = MDContent, Routes = context_routes)

@app.route("/<fold>")
def render_routes(fold):
	if fold not in context_routes:
		return redirect('/')

	folder_contents = os.listdir(os.path.join(context_routes_folder,fold))

	MDContent = []
	for md_file in folder_contents:
		with open(os.path.join(context_routes_folder,fold,md_file)) as mdfile:
			MDContent.append([markdown.markdown(mdfile.read(), extensions=['fenced_code','codehilite']),md_file,ctime(os.path.getctime(os.path.join(context_routes_folder,fold,md_file)))])
	return render_template('context_md.html',MDContent = MDContent)

for item in os.listdir(context_routes_folder):
	if not os.path.isfile(os.path.join(context_routes_folder,item)):
		context_routes.append(item)

if len(context_routes) == 0:
	context_routes = None


@app.route('/pagemanager', methods = ['GET','POST'])
@basic_auth.required
def pagemanager():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('A file needs to be specified!')
			return redirect(url_for('pagemanager'))

		file = request.files['file']

		if request.files['file'].filename.rsplit('.', 1)[1].lower() != 'md':
			flash('The file needs to have markdown extension!')
			return redirect(url_for('pagemanager'))
		try:
			markdown.markdown(file.read(), extensions=['fenced_code','codehilite'])
		except:
			flash('The content of the file is not markdown, wont be saved!')
			return redirect(url_for('pagemanager'))

		file.stream.seek(0)
	
		if os.path.isfile(os.path.join(context_routes_folder,request.form.get('destination'),file.filename)):
			if request.form.get('overwrite'):
				flash('Successfully overwritten the previous file called: {} in folder: {}'.format(file.filename,request.form.get('destination')))	
			else:
				flash('Aborting as overwrite was not allowed for file: {} in folder: {}'.format(file.filename,request.form.get('destination')))
		else:
			file.save(os.path.join(context_routes_folder,request.form.get('destination'),file.filename))
			flash('Successfully saved the file called: {} to folder: {}'.format(file.filename,request.form.get('destination')))
		
		return redirect(url_for('pagemanager'))

	else:
		return render_template('upload_form.html', options = context_routes)

@app.route("/foldermanager", methods = ['GET','POST'])
@basic_auth.required
def foldermanager():
	if request.method == 'POST':
		if not request.form.get('folder'):
			abort(403,"You cannot manage a folder without a name")

		if not request.form.get('action').lower() in ['create','delete']:
			abort(403,"Invalid action is specified!")

		action = request.form.get('action').lower()
		folder_to_manage = request.form.get('folder').lower()
		
		if folder_to_manage in ['foldermanager','pagemanager']:
			flash("This is a reserved name: {}, cannot use it!".format(folder_to_manage))
			return redirect(url_for('foldermanager'))

		if folder_to_manage in context_routes:
			if action == 'create':
				flash("Cannot create a folder that already exsists: {}".format(folder_to_manage))
			else:
				shutil.rmtree(os.path.join(context_routes_folder,folder_to_manage),ignore_errors=True)
				context_routes.remove(folder_to_manage)
				flash('Folder: || {} || deleted at: {}'.format(folder_to_manage, datetime.now()))
		else:
			if action == 'create':
				os.makedirs(os.path.join(context_routes_folder,folder_to_manage))
				context_routes.append(folder_to_manage)
				flash('Folder: || {} || created at: {}'.format(folder_to_manage, datetime.now()))
			else:
				flash("Cannot delete a nonexsisting folder like: {}".format(folder_to_manage))
				
		return redirect(url_for('foldermanager'))
			
	else:
		return render_template('folderer.html', exsisting = context_routes)
if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 8080, debug = True)