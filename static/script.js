let start = 0;
const filesPerRequest = 10;
let loading = false;


async function deleteFile(folder, filename, fileElement) {
    if (confirm("Voulez-vous vraiment supprimer ce fichier ?")) {
        try {
            const response = await fetch("/delete_file", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ folder: folder, filename: filename }),
            });

            const result = await response.json();

            if (response.ok && result.success) {
                fileElement.remove();
            } else {
                console.error(result.message);
                alert("Erreur : " + result.message);
            }
        } catch (error) {
            console.error("Erreur lors de la suppression du fichier : ", error);
            alert("Une erreur est survenue, veuillez réessayer plus tard.");
        }
    }
}

async function deleteFolder(folder) {
    if (confirm("Voulez-vous vraiment supprimer ce dossier et tout son contenu ?")) {
        try {
            const response = await fetch("/delete_folder", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ folder: folder }),
            });

            const result = await response.json();
            if (response.ok && result.success) {
                location.reload();
            } else {
                console.error(result.message);
                alert("Erreur : " + result.message);
            }
        } catch (error) {
            console.error("Erreur lors de la suppression du dossier : ", error);
        }
    }
}


async function loadFiles(folder) {
    if (loading) return;

    const encodedFolder = encodeURIComponent(folder);
    const response = await fetch(`/get_files?folder=${encodedFolder}&start=${start}`);
    const data = await response.json();

    if (data.files && data.files.length > 0) {
        data.files.forEach(file => {
            const fileElement = document.createElement('li');
            fileElement.innerHTML = `
                <a href="/uploads/${encodedFolder}/${file}" target="_blank">${file}</a>
                <img src="/uploads/${encodedFolder}/${file}" width="100">
                <button onclick="deleteFile('${folder}', '${file}', this.parentElement)" class="delete-btn">🗑</button>
            `;
            document.getElementById('file-list').appendChild(fileElement);
        });

        start += filesPerRequest;

        // Appeler la fonction pour charger les fichiers suivants
        loadFiles(folder);
    } else {
        loading = true; // Plus de fichiers à charger
    }
}

document.addEventListener("DOMContentLoaded", function () {
    loadFiles(selectedFolder);
});

function showRenameFolderModal(folder) {
    document.getElementById('renameFolderModal').style.display = 'block';
    document.getElementById('old-folder').value = folder;
}

function closeRenameFolderModal() {
    document.getElementById('renameFolderModal').style.display = 'none';
}
