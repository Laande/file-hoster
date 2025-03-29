from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import shutil

app = Flask(__name__)

BASE_DIR = "/home/hdd/uploads"
os.makedirs(BASE_DIR, exist_ok=True)

FILES_PER_REQUEST = 10

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

        elif "rename_folder" in request.form:
            old_folder = request.form["old_folder"]
            new_folder = request.form["new_folder"].strip()
            if new_folder:
                old_folder_path = os.path.join(BASE_DIR, old_folder)
                new_folder_path = os.path.join(BASE_DIR, new_folder)
                if os.path.exists(old_folder_path):
                    try:
                        os.rename(old_folder_path, new_folder_path)
                    except Exception as e:
                        return jsonify({"success": False, "message": f"Erreur lors du renommage du dossier : {str(e)}"}), 500
    
    folders = sorted([f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))])
    files = sorted(os.listdir(folder_path)) if selected_folder and os.path.exists(folder_path) else []

    return render_template("index.html", folders=folders, selected_folder=selected_folder, files=files)


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
        return jsonify({"files": files_to_send})
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
