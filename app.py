from flask import Flask, request, redirect, url_for, flash, render_template_string, send_file
import os
import shutil
import zipfile
import urllib.parse
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "organized"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- FILE TYPES ----------
FILE_TYPES = {
    'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    'Music': ['.mp3', '.wav', '.m4a'],
    'Videos': ['.mp4', '.mkv', '.avi', '.mov'],
    'Applications': ['.exe', '.msi', '.apk'],
    'Compressed': ['.zip', '.rar', '.7z'],
    'Others': []
}

# ---------- HTML TEMPLATE ----------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>File Management Simulator</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: linear-gradient(120deg, #0f2027, #203a43, #2c5364); color: #fff; font-family: 'Poppins', sans-serif; min-height: 100vh; overflow-x: hidden; }
    .sidebar { width: 250px; background: rgba(255,255,255,0.08); height: 100vh; position: fixed; left: 0; top: 0; padding-top: 2rem; backdrop-filter: blur(15px); border-right: 1px solid rgba(255,255,255,0.2); }
    .sidebar a { display: block; padding: 12px 20px; color: #fff; opacity: 0.8; text-decoration: none; border-radius: 12px; margin: 4px 12px; transition: all 0.2s ease; }
    .sidebar a:hover, .sidebar a.active { background: rgba(255,255,255,0.15); opacity: 1; transform: scale(1.02); }
    .main { margin-left: 270px; padding: 3rem; }
    .card { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 20px; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2); }
    .file-card { background: rgba(255,255,255,0.08); padding: 1rem; border-radius: 12px; text-align: center; transition: all 0.2s ease; }
    .file-card:hover { background: rgba(255,255,255,0.15); transform: translateY(-4px); }
    .btn { background: linear-gradient(to right, #f9d423, #ff4e50); color: #000; padding: 10px 18px; border-radius: 10px; font-weight: 600; }
    input, button { outline: none !important; }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <div class="sidebar">
    <h1 class="text-2xl font-bold text-center mb-6">🗂 Simulator</h1>
    <a href="{{ url_for('index') }}" class="{% if not category %}active{% endif %}">🏠 All Files</a>
    {% for cat in FILE_TYPES.keys() %}
      <a href="{{ url_for('index', category=cat) }}" class="{% if category == cat %}active{% endif %}">📁 {{ cat }}</a>
    {% endfor %}
    <hr class="border-gray-500/30 my-4">
    <a href="{{ url_for('index') }}#upload">⬆ Upload Files</a>
    <a href="{{ url_for('index') }}#path">🗃 Organize Folder</a>
  </div>

  <!-- Main -->
  <div class="main">
    <div class="card mb-10">
      <h1 class="text-4xl font-extrabold text-yellow-400 mb-3">File Management & Organizing Simulator</h1>
      <p class="text-gray-300 mb-4">Upload, organize, rename, and delete your files effortlessly ⚙️</p>

      {% if get_flashed_messages(with_categories=true) %}
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% for category, msg in messages %}
            {% if msg %}
              <div class="mb-3 p-3 rounded-lg {% if category == 'success' %}bg-green-600/40{% else %}bg-red-600/40{% endif %}">
                {{ msg | safe }}
              </div>
            {% endif %}
          {% endfor %}
        {% endwith %}
      {% endif %}

      <!-- Upload -->
      <form id="upload" action="{{ url_for('upload') }}" method="POST" enctype="multipart/form-data" class="mb-6 space-y-3">
        <input type="file" name="files[]" multiple class="block w-full p-3 bg-white/10 rounded-lg">
        <button type="submit" class="btn w-full">Organize Uploaded Files</button>
      </form>

      <!-- Organize existing folder -->
      <form id="path" action="{{ url_for('organize_path') }}" method="POST" class="space-y-3">
        <input type="text" name="folder_path" placeholder="Enter folder path (e.g., D:/Downloads)" required class="block w-full p-3 bg-white/10 rounded-lg">
        <button type="submit" class="btn w-full">Organize Existing Folder</button>
      </form>
    </div>

    <!-- File Grid -->
    {% if files %}
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-5">
        {% for file in files %}
          <div class="file-card">
            <p class="font-semibold text-yellow-300 truncate">{{ file.name }}</p>
            <p class="text-xs text-gray-400 mb-2">{{ file.rel_folder }}</p>
            <div class="flex justify-center space-x-2">
              <form action="{{ url_for('rename_file') }}" method="POST" class="inline-flex space-x-1">
                <input type="hidden" name="old_path" value="{{ file.path }}">
                <input type="text" name="new_name" placeholder="Rename" class="w-24 p-1 rounded bg-white/10 text-xs text-white">
                <button type="submit" class="text-yellow-400 text-sm">✏️</button>
              </form>
              <form action="{{ url_for('delete_file') }}" method="POST" class="inline">
                <input type="hidden" name="file_path" value="{{ file.path }}">
                <button type="submit" class="text-red-400 text-sm">🗑️</button>
              </form>
            </div>
          </div>
        {% endfor %}
      </div>
    {% else %}
      <p class="text-gray-400">No files found. Upload or organize a folder to begin.</p>
    {% endif %}
  </div>
</body>
</html>
"""

# ---------- CORE FUNCTIONS ----------
def organize_files(source_folder, output_folder):
    """Organizes files into folders by type."""
    for folder in FILE_TYPES.keys():
        os.makedirs(os.path.join(output_folder, folder), exist_ok=True)

    for root, _, files in os.walk(source_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isdir(file_path):
                continue

            # Extract ZIP files automatically
            _, ext = os.path.splitext(filename)
            ext = ext.lower().strip()
            if ext == '.zip':
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(root)
                    os.remove(file_path)
                    continue
                except Exception as e:
                    print(f"Failed to extract {filename}: {e}")

            moved = False
            for folder_name, extensions in FILE_TYPES.items():
                if ext in [e.lower() for e in extensions]:
                    shutil.move(file_path, os.path.join(output_folder, folder_name, filename))
                    moved = True
                    break
            if not moved:
                shutil.move(file_path, os.path.join(output_folder, 'Others', filename))


def list_files_in_directory(directory, category=None):
    """Recursively lists all files in organized folder, filtered by category."""
    file_list = []
    if not os.path.exists(directory):
        return file_list

    for root, _, files in os.walk(directory):
        for f in files:
            full_path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            matched_category = next((k for k, exts in FILE_TYPES.items() if ext in [e.lower() for e in exts]), 'Others')
            if category and matched_category != category:
                continue
            file_list.append({
                "name": f,
                "path": full_path,
                "url_path": urllib.parse.quote(full_path, safe=''),
                "rel_folder": matched_category
            })
    return file_list


def zip_folder(folder_path):
    """Zips a folder."""
    base_name = os.path.basename(folder_path.rstrip("/\\"))
    zip_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', folder_path)
    return zip_path

# ---------- ROUTES ----------
@app.route("/")
def index():
    category = request.args.get("category")
    files = list_files_in_directory(OUTPUT_FOLDER, category)
    return render_template_string(HTML_TEMPLATE, FILE_TYPES=FILE_TYPES, files=files, category=category)

@app.route("/upload", methods=["POST"])
def upload():
    if "files[]" not in request.files:
        flash("No files selected!", "error")
        return redirect(url_for("index"))

    files = request.files.getlist("files[]")
    if not files:
        flash("No files selected!", "error")
        return redirect(url_for("index"))

    session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_folder = os.path.join(UPLOAD_FOLDER, f"session_{session_id}")
    os.makedirs(temp_folder, exist_ok=True)

    for file in files:
        if file.filename:
            file.save(os.path.join(temp_folder, secure_filename(file.filename)))

    output_dir = os.path.join(OUTPUT_FOLDER, f"organized_{session_id}")
    os.makedirs(output_dir, exist_ok=True)
    organize_files(temp_folder, output_dir)
    shutil.rmtree(temp_folder)  # clean up temp folder

    flash("✅ Files uploaded and organized successfully!", "success")
    return redirect(url_for("index"))

@app.route("/organize_path", methods=["POST"])
def organize_path():
    folder_path = request.form.get("folder_path")
    if not folder_path or not os.path.exists(folder_path):
        flash("⚠️ Invalid folder path!", "error")
        return redirect(url_for("index"))

    session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = os.path.join(OUTPUT_FOLDER, f"organized_{session_id}")
    os.makedirs(output_dir, exist_ok=True)
    organize_files(folder_path, output_dir)

    flash(f"✅ Folder '{folder_path}' organized successfully!", "success")
    return redirect(url_for("index"))

@app.route("/rename_file", methods=["POST"])
def rename_file():
    old_path = request.form.get("old_path")
    new_name = request.form.get("new_name")
    if not old_path or not new_name:
        flash("⚠️ Missing details for rename.", "error")
        return redirect(url_for("index"))

    folder = os.path.dirname(old_path)
    new_path = os.path.join(folder, secure_filename(new_name))
    try:
        os.rename(old_path, new_path)
        flash(f"✅ Renamed to '{new_name}'", "success")
    except Exception as e:
        flash(f"⚠️ Rename failed: {e}", "error")
    return redirect(url_for("index"))

@app.route("/delete_file", methods=["POST"])
def delete_file():
    file_path = request.form.get("file_path")
    if not file_path or not os.path.exists(file_path):
        flash("⚠️ File not found!", "error")
        return redirect(url_for("index"))
    try:
        os.remove(file_path)
        flash("🗑️ File deleted successfully!", "success")
    except Exception as e:
        flash(f"⚠️ Delete failed: {e}", "error")
    return redirect(url_for("index"))

@app.route("/download/<folder_name>")
def download_folder(folder_name):
    folder_path = os.path.join(OUTPUT_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        flash("Folder not found!", "error")
        return redirect(url_for("index"))

    zip_path = zip_folder(folder_path)
    return send_file(zip_path, as_attachment=True)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
