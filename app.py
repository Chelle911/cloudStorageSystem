from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages

# Simulate storage with a simple JSON file
STORAGE_FILE = 'storage.json'

def load_storage():
    files_env = os.environ.get("CLOUD_FILES")
    if files_env:
        try:
            return json.loads(files_env)
        except json.JSONDecodeError:
            return {"files": []}  # Return proper structure

    if not os.path.exists(STORAGE_FILE):  # Use constant
        return {"files": []}  # Return proper structure
    try:
        with open(STORAGE_FILE, "r") as f:  # Use constant
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"files": []}  
        
def save_storage(storage):
    os.environ["CLOUD_FILES"] = json.dumps(storage)
    
    try:
        with open("storage.json", "w") as f:
            json.dump(storage, f, indent=2)
    except Exception as e:
        print(f"Error saving to file (this is expected in production): {e}")
    
    return True

@app.route('/')
def index():
    storage = load_storage()
    return render_template('index.html', files=storage['files'])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_size = len(file.read())  # Get file size in bytes
        file.seek(0)  # Reset file pointer after reading
        
        # In a real app, you'd save the file here
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Add file to storage
        storage = load_storage()
        new_file = {
            'id': len(storage['files']) + 1,
            'name': filename,
            'size': file_size,
            'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mime_type': file.content_type
        }
        storage['files'].append(new_file)
        save_storage(storage)
        
        flash(f'File {filename} uploaded successfully!')
        return redirect(url_for('index'))

@app.route('/simulate_upload', methods=['POST'])
def simulate_upload():
    filename = request.form.get('filename')
    if not filename:
        flash('No filename provided')
        return redirect(url_for('index'))
    
    storage = load_storage()
    new_file = {
        'id': len(storage['files']) + 1,
        'name': filename,
        'size': 1024,  # Simulated file size
        'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'mime_type': 'application/octet-stream'  # Default mime type
    }
    storage['files'].append(new_file)
    save_storage(storage)
    
    flash(f'File {filename} uploaded successfully!')
    return redirect(url_for('index'))

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    storage = load_storage()
    for i, file in enumerate(storage['files']):
        if file['id'] == file_id:
            deleted_file = storage['files'].pop(i)
            save_storage(storage)
            flash(f'File {deleted_file["name"]} deleted successfully!')
            break
    return redirect(url_for('index'))

@app.route('/update/<int:file_id>', methods=['POST'])
def update_file(file_id):
    new_name = request.form.get('new_name')
    if not new_name:
        flash('No new name provided')
        return redirect(url_for('index'))
    
    storage = load_storage()
    for file in storage['files']:
        if file['id'] == file_id:
            file['name'] = new_name
            file['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_storage(storage)
            flash(f'File renamed to {new_name} successfully!')
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
