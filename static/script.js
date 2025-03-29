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
            alert("Une erreur est survenue, veuillez réessayer plus tard.");
        }
    }
}

async function renameFolder(oldFolder, newFolder) {
    if (!newFolder.trim()) {
        alert("Le nom du dossier ne peut pas être vide");
        return;
    }
    
    try {
        const response = await fetch("/rename_folder", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ old_folder: oldFolder, new_folder: newFolder }),
        });

        const result = await response.json();
        if (response.ok && result.success) {
            if (result.redirect_url) {
                window.location.href = result.redirect_url;
            } else {
                location.reload();
            }
        } else {
            console.error(result.message);
            alert("Erreur : " + result.message);
        }
    } catch (error) {
        console.error("Erreur lors du renommage du dossier : ", error);
        alert("Une erreur est survenue, veuillez réessayer plus tard.");
    }
}

async function loadFiles(folder) {
    if (loading) return;

    const encodedFolder = encodeURIComponent(folder);
    const response = await fetch(`/get_files?folder=${encodedFolder}&start=${start}`);
    const data = await response.json();

    if (data.files && data.files.length > 0) {
        data.files.forEach(file => {
            const fileName = typeof file === 'object' ? file.name : file;
            const fileSize = typeof file === 'object' ? file.size : '';
            const sizeDisplay = fileSize ? ` (${fileSize})` : '';
            
            const fileExtension = fileName.split('.').pop().toLowerCase();
            const isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExtension);
            
            const fileElement = document.createElement('li');
            fileElement.innerHTML = `
                <a href="/uploads/${encodedFolder}/${fileName}" target="_blank">${fileName}${sizeDisplay}</a>
                ${isImage ? `<img src="/uploads/${encodedFolder}/${fileName}" width="100">` : ''}
                <button onclick="deleteFile('${folder}', '${fileName}', this.parentElement)" class="delete-btn"></button>
            `;
            document.getElementById('file-list').appendChild(fileElement);
        });

        start += filesPerRequest;

        loadFiles(folder);
    } else {
        loading = true;
    }
}

function showRenameFolderModal(folder) {
    document.getElementById('renameFolderModal').style.display = 'block';
    document.getElementById('old-folder').value = folder;
    document.getElementById('new-folder').value = folder;
    document.getElementById('new-folder').focus();
    document.getElementById('new-folder').select();
}

function closeRenameFolderModal() {
    document.getElementById('renameFolderModal').style.display = 'none';
}

document.addEventListener("DOMContentLoaded", function() {
    if (typeof selectedFolder !== 'undefined' && selectedFolder) {
        loadFiles(selectedFolder);
    }
    
    const renameForm = document.getElementById('rename-form');
    if (renameForm) {
        renameForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const oldFolder = document.getElementById('old-folder').value;
            const newFolder = document.getElementById('new-folder').value;
            renameFolder(oldFolder, newFolder);
        });
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeRenameFolderModal();
        }
    });
});
