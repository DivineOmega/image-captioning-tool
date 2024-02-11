from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    images = []
    current_dir = app.config['UPLOAD_FOLDER']
    if os.path.isdir(current_dir):
        for filename in os.listdir(current_dir):
            if allowed_file(filename):
                images.append(filename)
    else:
        # Handle case where current directory is not valid
        pass
    return render_template('index.html', images=images, get_caption_for_image=get_caption_for_image, current_dir=current_dir)


def sanitize_filename(filename):
    # Replace or remove potentially unsafe characters
    # This is a basic example; you might need to expand this list based on your requirements
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '')

    # Remove any path traversal attempts
    filename = filename.replace('..', '')

    # You might want to add more sanitization rules here depending on your needs

    return filename

@app.route('/save_caption', methods=['POST'])
def save_caption():
    caption = request.form['caption']
    original_filename = request.form['filename']
    current_dir = app.config['UPLOAD_FOLDER']

    # Sanitize the filename to keep spaces and brackets but remove other potentially unsafe characters
    filename = sanitize_filename(original_filename)

    caption_path = os.path.join(current_dir, os.path.splitext(filename)[0] + '.txt')
    with open(caption_path, 'w') as f:
        f.write(caption)

    return '', 204


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def get_caption_for_image(image_filename):
    # Change the image file extension to .txt to find the corresponding caption file
    base, _ = os.path.splitext(image_filename)
    caption_filename = base + '.txt'
    caption_path = os.path.join(app.config['UPLOAD_FOLDER'], caption_filename)

    # Try to read the caption from the file
    try:
        with open(caption_path, 'r') as f:
            return f.read()
    except IOError:
        # If the caption file doesn't exist or can't be read, return an empty string
        return ""

@app.route('/change_directory', methods=['POST'])
def change_directory():
    new_directory = request.form.get('new_directory')
    if os.path.isdir(new_directory):
        app.config['UPLOAD_FOLDER'] = new_directory
    else:
        # Handle the case where the new directory is invalid (e.g., flash a message)
        pass
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
