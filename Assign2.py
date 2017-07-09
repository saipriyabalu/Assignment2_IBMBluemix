#References: https://pypi.python.org/pypi/cloudant/2.0.0a
#http://ishwortimilsina.com/upload-file-cloudant-nosql-db-using-python-flask
#https://docs.python.org/2/howto/unicode.html
#http://python-cloudant.readthedocs.io/en/latest/getting_started.html
#https://pymotw.com/2/codecs/



# Import statements
import os, time
from flask import Flask, request
from base64 import b64encode
from cloudant.client import Cloudant

#Enter user name and password
username= "b4211360-a7c0-4e19-89c0-e77acf0ba0ad-bluemix"
password= "f6259e862b866baad033a11fe4511e38dbb7882567ebde4d6662b75653b87bd3"

# Connect to cloudant
client = Cloudant(username, password, url='https://b4211360-a7c0-4e19-89c0-e77acf0ba0ad-bluemix:f6259e862b866baad033a11fe4511e38dbb7882567ebde4d6662b75653b87bd3@b4211360-a7c0-4e19-89c0-e77acf0ba0ad-bluemix.cloudant.com')
client.connect()
my_database = client['my_storage']
APPROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/list', methods=['POST'])
def list():
    file = "No Files stored"
    files_inmydb = ""
    file_header = ""
    for doc in my_database:
        file = ""
        file_header= '<h2>Files in the database:</h2><ol>'
        files_inmydb = files_inmydb + '<li>File: {0}</br>\n Version: {1}</br>\n Last Modified: {2}'.format(doc['file_name'], doc['version number'], doc['last modified date']) + '</li></p>'
    return file + file_header + files_inmydb

@app.route('/upload', methods=['POST'])
def upload():
    enter_filename = request.files['enter_filename']
    file_name = enter_filename.filename
    content = enter_filename.read()
    uploadedcontent = b64encode(enter_filename.read())
    base64_string = uploadedcontent.decode('utf-8')
    lastmodified = time.ctime(os.path.getmtime(file_name))
    version_num = 0
    for document in my_database:
        if (file_name == document['file_name']):
            if (content.decode('utf-8') == document['content']):
                return "You have entered the same file name"
    for document in my_database:
        if (file_name == document['file_name'] and not content.decode('utf-8') == document['content']):
            version = document['version number']
            if int(version) > version_num:
                version_num = int(version)
    if version_num == 0:
        data = {'file_name': file_name, 'content': content.decode('utf-8'), 'last modified date': lastmodified,'version number': '1'}
        doc = my_database.create_document(data)
    else:
        data = {'file_name': file_name, 'content': content.decode('utf-8'), 'last modified date': lastmodified,'version number': int(version_num) + 1}
        doc = my_database.create_document(data)

    if doc.exists():
        return "Document uploaded successfully!"

@app.route('/delete', methods=['POST'])
def delete():
    version_number = request.form['version number']
    file_name = request.form['filename']
    for document in my_database:
        if (document['file_name'] == file_name):
            if (document['version number'] == version_number):
                document.delete()
                displaymessage = "Document deleted successfully"
                break
        else:
            displaymessage = "File not found"
    return displaymessage

@app.route('/download', methods=['POST'])
def download():
    file_name = request.form['filename']
    version_number = request.form['version number']
    for document in my_database:
        if (document['file_name'] == file_name):
            if (document['version number'] == version_number):
                downloaddoc = "Document downloaded successfully!"
                with open(file_name, 'w') as outfile:
                    outfile.write(document['content'])
                break
        else:
            downloaddoc = "File is not found"
    return downloaddoc

if __name__ == "__main__":
    app.run(debug=True)