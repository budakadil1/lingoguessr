import boto3, random, os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask import current_app as app

main = Blueprint('main', __name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_S3_REGION")
)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('main.index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.index'))

    if file and file.filename.endswith('.mp3'):
        filename = secure_filename(file.filename)
        s3.upload_fileobj(file, app.config['AWS_S3_BUCKET'], filename)
        flash('File uploaded successfully')
    else:
        flash('Only .mp3 files are allowed')

    return redirect(url_for('main.index'))

@main.route('/random-mp3')
def random_mp3():
    response = s3.list_objects_v2(Bucket=app.config['AWS_S3_BUCKET'])
    files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.mp3')]
    
    if not files:
        return "No MP3 files found", 404

    random_file = random.choice(files)
    url = s3.generate_presigned_url('get_object', Params={
        'Bucket': app.config['AWS_S3_BUCKET'],
        'Key': random_file
    }, ExpiresIn=3600)
    
    return redirect(url)
