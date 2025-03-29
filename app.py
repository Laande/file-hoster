from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
import os
import shutil

app = Flask(__name__)

BASE_DIR = "/home/hdd/uploads"
os.makedirs(BASE_DIR, exist_ok=True)

FILES_PER_REQUEST = 10

def get_size_format(size_bytes):
    """Convertit les octets en format lisible (KB, MB, GB)"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_folder_size(folder_path):
    """Calcule la taille totale d'un dossier"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

@app.route("/", methods=["GET", "POST"])
def index():
    selected_folder = request.args.get("folder", "")
    folder_path = os.path.join(BASE_DIR, selected_folder) if selected_folder else BASE_DIR
    
    if request.method == "POST":
        if "new_folder" in request.form:
            new_folder = request.form["new_folder"].strip()
            if new_folder:
                os.makedirs(os.path.join(BASE_DIR, new_folder), exist_ok=True)

        elif "files" in request.files and selected_folder:
            files = request.files.getlist("files")
            os.makedirs(folder_path, exist_ok=True)
            for file in files:
                if file.filename:
                    file.save(os.path.join(folder_path, file.filename))
    
    folders = sorted([f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))])
    
    folders_with_count = []
    for folder in folders:
        folder_path_count = os.path.join(BASE_DIR, folder)
        file_count = len([f for f in os.listdir(folder_path_count) if os.path.isfile(os.path.join(folder_path_count, f))])
        folder_size = get_folder_size(folder_path_count)
        folder_size_formatted = get_size_format(folder_size)
        folders_with_count.append({
            "name": folder, 
            "count": file_count,
            "size": folder_size_formatted
        })
    
    initial_files = []
    if selected_folder and os.path.exists(folder_path):
        pass

    return render_template("index.html", folders=folders_with_count, selected_folder=selected_folder, files=initial_files)


@app.route("/uploads/<folder>/<filename>")
def uploaded_file(folder, filename):
    return send_from_directory(os.path.join(BASE_DIR, folder), filename)


@app.route("/get_files", methods=["GET"])
def get_files():
    folder = request.args.get("folder")
    start = int(request.args.get("start", 0))
    end = start + FILES_PER_REQUEST
    folder_path = os.path.join(BASE_DIR, folder)
    
    if os.path.exists(folder_path):
        all_files = sorted(os.listdir(folder_path))
        files_to_send = all_files[start:end]
        
        files_with_size = []
        for file in files_to_send:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files_with_size.append({
                    "name": file,
                    "size": get_size_format(file_size)
                })
        
        return jsonify({"files": files_with_size})
    else:
        return jsonify({"files": []})

@app.route("/delete_file", methods=["POST"])
def delete_file():
    data = request.get_json()
    folder = data.get("folder")
    filename = data.get("filename")
    file_path = os.path.join(BASE_DIR, folder, filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({"success": True, "message": f"Fichier {filename} supprimé avec succès!"}), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Erreur lors de la suppression du fichier : {str(e)}"}), 500
    else:
        return jsonify({"success": False, "message": "Fichier non trouvé."}), 404

@app.route("/delete_folder", methods=["POST"])
def delete_folder():
    data = request.get_json()
    folder = data.get("folder")
    folder_path = os.path.join(BASE_DIR, folder)
    
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            return jsonify({"success": True, "message": f"Dossier {folder} supprimé avec succès!"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Erreur lors de la suppression du dossier : {str(e)}"})
    else:
        return jsonify({"success": False, "message": "Dossier non trouvé."})

@app.route("/rename_folder", methods=["POST"])
def rename_folder():
    data = request.get_json()
    old_folder = data.get("old_folder")
    new_folder = data.get("new_folder")
    
    old_folder_path = os.path.join(BASE_DIR, old_folder)
    new_folder_path = os.path.join(BASE_DIR, new_folder)
    
    os.rename(old_folder_path, new_folder_path)
    return jsonify({
        "success": True, 
        "redirect_url": url_for('index', folder=new_folder)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
