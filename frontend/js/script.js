const BACKEND_URL = "http://localhost:8000"
const API_VERSION_PREFIX = "/api/v1"
var dropZone;
var evtSource = null;

window.onload = function fillParameters() {
    //fillAvailableModels();
    //fillAvailableTranscriptions();
}

window.onbeforeunload = function closeWindow() {
    closeEventSource();
}

function fillAvailableTranscriptions(element) {
    let endpoint = `${API_VERSION_PREFIX}/list/transcripts`;

    const options = {
        method: 'GET'
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            for(let model of data) {
                const newOption = document.createElement("option");
                newOption.value = model;
                newOption.text = model;
                element.appendChild(newOption);
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function setNavBarActive(element) {
    document.getElementsByClassName('navActive')[0].classList.remove('navActive');
    element.classList.add('navActive');

    closeEventSource();
}

function closeEventSource() {
    if(evtSource) {
        console.log("Closing SSE");
        evtSource.close();
        evtSource = null;
    }
}

function loadPage(event, url, callback = function() {}) {
    event.preventDefault();

    fetch(url)
        .then(response => {
        if (!response.ok) throw new Error('Page not found');
            return response.text();
        })
        .then(html => {
            document.getElementById('content').innerHTML = html;
            callback();
        })
        .catch(err => {
            console.error('Error loading page:', err);
            document.getElementById('content').innerHTML = '<h1>Error</h1><p>Could not load the page.</p>';
        });
}

function loadDocumentsPage(event, url) {
    loadPage(event, url, function () {
        setNavBarActive(document.getElementById('navbarDocuments'));
        fillFilesTable("/api/v1/list/documents", document.querySelector("#filesTable tbody"), "document");
        document.getElementById('uploadCard').addEventListener('click', function() {
            document.getElementById('fileInput').click();
        });
        document.getElementById('fileInput').addEventListener('change', function(event) {
            uploadDocument(event.target.files[0], "/api/v1/upload/document", ['pdf']);
        });
        dropZone = document.getElementById("uploadCard");
    });
}

function loadTranscriptsPage(event, url) {
    loadPage(event, url, function () {
        setNavBarActive(document.getElementById('navbarTranscripts'));
        fillFilesTable("/api/v1/list/transcripts", document.querySelector("#filesTable tbody"), "transcript");
        document.getElementById('uploadCard').addEventListener('click', function() {
            document.getElementById('fileInput').click();
        });
        document.getElementById('fileInput').addEventListener('change', function(event) {
            uploadDocument(event.target.files[0], "/api/v1/upload/transcript", ['txt', 'srt', 'vtt']);
        });
        dropZone = document.getElementById("uploadCard");
    });
}

function loadSettingsPage(event, url) {
    loadPage(event, url, function () {
        setNavBarActive(document.getElementById('navbarSettings'));
        fillCurrentSettingsValues();
    });
}

function loadHomePage(event, url) {
    loadPage(event, url, function () {
        setNavBarActive(document.getElementById('navbarHome'));
    });
}

function loadSummarizeHomePage(event, url) {
    loadPage(event, url, function () {
        setNavBarActive(document.getElementById('navbarSummarize'));
    });
}

function loadSummarizationPage(event, url) {
    loadPage(event, url, function () {
        setNavBarActive(document.getElementById('navbarSummarize'));
        fillAvailableTranscriptions(document.getElementById("transcriptList"));
        startSseConnection();
    });
}

function loadProcessedFilesPage(event, url) {
    loadPage(event, url, function () {
        setNavBarActive(document.getElementById('navbarProcessedFiles'));
        fillFilesTable("/api/v1/list/processed-files", document.querySelector("#filesTable tbody"), "processed-file");
    });
}

function fillFilesTable(endpoint, tableBody, downloadAndRemoveEndpoint) {
    const options = {
        method: 'GET'
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(`Data retrieved: ${data}`);
            let i = 1;

            data.forEach(name => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <th scope="row">${i++}</th>
                    <td>${name}</td>
                    <td>
                    <button type="button" class="btn btn-primary" onclick="downloadDocument(this, \`${downloadAndRemoveEndpoint}\`)">
                        Download
                        <i class="bi bi-file-earmark-arrow-down"></i>
                    </button>
                    </td>
                    <td>
                        <button type="button" class="btn btn-danger" onclick="removeDocument(this, \`${downloadAndRemoveEndpoint}\`)">
                            Remove
                            <i class="bi bi-file-earmark-x"></i>
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            alert(`There was a problem when fetching the list of documents: ${error}`);
        });
}

function refreshDocumentsFilesTable() {
    document.querySelector("#filesTable tbody").innerHTML = '';
    fillFilesTable("/api/v1/list/documents", document.querySelector("#filesTable tbody"), "document");
}

function refreshTranscriptFilesTable() {
    document.querySelector("#filesTable tbody").innerHTML = '';
    fillFilesTable("/api/v1/list/transcripts", document.querySelector("#filesTable tbody"), "transcript");
}

function uploadDocument(file, endpoint, validExtensions) {
    if (!file) {
        alert("Error uploading file, make sure it exists");
        return;
    }
    console.log(`Uploading file ${file.name}`);

    //Check if file type is supported
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!validExtensions.includes(fileExtension)) {
        alert("Invalid file type. Please upload a .pdf file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file, file.name);

    const options = {
        method: 'POST',
        body: formData
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(responseData => {
            alert('File successfully uploaded!')
            console.log(responseData);
            if(endpoint.includes('transcript'))
                refreshTranscriptFilesTable();
            else
                refreshDocumentsFilesTable();
        })
        .catch(error => {
            alert(`There was a problem with the network when uploading the document: ${error}`);
        });
}

function dropDocumentHandler(event) {
    dropFileHandler(event, "/api/v1/upload/document", ['pdf']);
}

function dropTranscriptHandler(event) {
    dropFileHandler(event, "/api/v1/upload/transcript", ['txt', 'srt', 'vtt']);
}

function dropFileHandler(event, endpoint, validExtensions) {
    //Prevent default behavior (Prevent file from being opened)
    event.preventDefault();

    if (event.dataTransfer.items) {
        // Use DataTransferItemList interface to access the file(s)
        [...event.dataTransfer.items].forEach((item, i) => {
          // If dropped items aren't files, reject them
          if (item.kind === "file") {
            uploadDocument(item.getAsFile(), endpoint, validExtensions);
          }
        });
      } else {
        // Use DataTransfer interface to access the file(s)
        [...event.dataTransfer.files].forEach((file, i) => {
            uploadDocument(file, endpoint, validExtensions);
        });
    }
    dropZone.classList.remove('drag-over');
}

function dragOverHandler(event) {
    event.preventDefault();
    dropZone.classList.add('drag-over');
}

function dragLeaveHandler(event) {
    dropZone.classList.remove('drag-over');
}

function downloadDocument(button, parcialEndpoint) {
    const row = button.closest('tr');
    const fileName = row.querySelector('td').textContent.trim();
    const endpoint = `/api/v1/download/${parcialEndpoint}/${fileName}`;

    const options = {
        method: 'GET'
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(data => {
            //Create a URL for the Blob
            const blobUrl = URL.createObjectURL(data);

            //Create a temporary anchor element
            const a = document.createElement("a");
            a.href = blobUrl;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // Revoke the Blob URL to free up memory
            URL.revokeObjectURL(blobUrl);
        })
        .catch(error => {
            alert(`There was a problem downloading the document: ${error}`);
        });
}

function removeDocument(button, parcialEndpoint) {
    const row = button.closest('tr');
    const fileName = row.querySelector('td').textContent.trim();
    if(!confirm(`Are you sure you want to remove the document "${fileName}"?`))
        return;
    const endpoint = `/api/v1/remove/${parcialEndpoint}`;

    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "file": fileName
        })
    };

    console.log(options);

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            alert(`Successfully removed the file ${fileName}`);
            if(endpoint.includes('transcript'))
                refreshTranscriptFilesTable();
            else
                refreshDocumentsFilesTable();
        })
        .catch(error => {
            alert(`There was a problem when trying to remove the document: ${error}`);
        });
}

//Settings
function updateRangeValue(inputElement, outputElementId) {
    document.getElementById("saveSettingsChanges").disabled = false;
    const outputElement = document.getElementById(outputElementId);
    outputElement.textContent = inputElement.value;
}

function fillCurrentSettingsValues() {
    const endpoint = '/api/v1/settings'
    const options = {
        method: 'GET'
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            document.getElementById("topPLabel").innerHTML = data["top_p"]
            document.getElementById("topP").value = data["top_p"]
            document.getElementById("temperatureLabel").innerHTML = data["temperature"]
            document.getElementById("temperature").value = data["temperature"]
            document.getElementById("debugTraces").value = data["debug_traces"]

            for(let model of data["availableModels"]) {
                const newOption = document.createElement("option");
                newOption.value = model;
                newOption.text = model;
                if(model == data["selectedModel"]) {
                    newOption.selected = true;
                }
                document.getElementById("modelSelect").appendChild(newOption);
            }
            document.getElementById("loadingSpinner").style.visibility = "hidden";
        })
        .catch(error => {
            alert(`There was a problem when fetching the list of documents: ${error}`);
        });
}

function sendSettingsValues() {
    const endpoint = '/api/v1/settings'

    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "selectedModel": document.getElementById("topP").value,
            "temperature": document.getElementById("temperature").value,
            "topP": document.getElementById("topP").value,
            "debugTraces": document.getElementById("debugTraces").value
        })
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            alert("Successfully changed the settings");
            document.getElementById("saveSettingsChanges").disabled = true;
        })
        .catch(error => {
            alert(`There was a problem when trying to send the settings values: ${error}`);
        });
}

function searchAndDownloadModel() {
    const endpoint = '/api/v1/model/download'
    const model = document.getElementById("newModel").value;
    document.getElementById("downloadLoadingSpinner").style.visibility = "visible";

    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "model": model
        })
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            alert("Model successfully downloaded");
            document.getElementById("downloadLoadingSpinner").style.visibility = "hidden";
        })
        .catch(error => {
            alert(`There was a problem when trying to download the model: ${error}`);
        });
}

function startSseConnection() {
    evtSource = new EventSource(BACKEND_URL + '/stream/v1/stream');
    evtSource.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('Received SSE message:', message);
        clearJobStatusComponent();
        if(message.task.processing) {
            toggleProcessingJob(message.task.transcript, message.task.task_name, message.task.progress)
        }
        if(!message.task.processing && message.task.state == "Ready") {
            console.log("toggle processed job");
            toggleProcessedJob(message.task.transcript, message.task.task_name, message.task.processed_filename);
        }
        else if(!message.task.processing) {
            console.log("toggle not processing job");
            toggleNotProcessingJob();
        }
    };
}

function clearJobStatusComponent() {
    console.log("cleaning component");
    document.getElementById("jobStatusContainer").innerHTML = "";
}

function getProcessingJobStatusComponent(transcriptName, taskName, progress) {
    return `
    <div id="status container">
        <div class="mb-3">
            <div class="d-flex justify-content-center align-items-center mt-3">
                <div class="spinner-border text-warning" id="processingLoadingSpinner" role="status">
                    <span class="sr-only"></span>
                </div>
            </div>
        </div>
        <div class="mb-3 d-flex justify-content-center">
            <span id="jobState">Processing ${taskName} for transcript: ${transcriptName}</span>
        </div>
        <div class="mb-3 d-flex justify-content-center">
            <span id="jobState">Remaining time to finish: <strong> ~${progress} seconds </strong></span>
        </div>
    </div>
    `
}

function getNotProcessingStatusComponent() {
    return `
    <div id="status container">
        <div class="mb-3 d-flex justify-content-center">
            <strong class="mr-2"> Status: &nbsp</strong>
            <span class="badge bg-success ml-2">Ready to process</span>
        </div>
    </div>
    `
}

function getProcessedStatusComponent(taskName, transcriptName, processed_filename) {
    return `
    <div id="status container d-flex justify-content-center">
        <div class="mb-3 d-flex justify-content-center">
            <span id="jobState">${taskName} of transcript: ${transcriptName} is ready :)</span>
        </div>
        <div class="mb-3 d-flex justify-content-center">
            <button type="button" class="btn btn-primary mr-3" onclick="downloadProcessedFile(\`${processed_filename}\`)">
                Download file
                <i class="bi bi-file-earmark-arrow-down"></i>
            </button>
            <button type="button" class="btn btn-primary" onclick="clearProcessedFile(\`${processed_filename}\`)">
                Clear
            </button>
        </div>
    </div>
    `
}

function downloadProcessedFile(processed_file) {
    const endpoint = `/api/v1/generate/download/${processed_file}`;

    const options = {
        method: 'GET'
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(data => {
            //Create a URL for the Blob
            const blobUrl = URL.createObjectURL(data);

            //Create a temporary anchor element
            const a = document.createElement("a");
            a.href = blobUrl;
            a.download = processed_file;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // Revoke the Blob URL to free up memory
            URL.revokeObjectURL(blobUrl);
        })
        .catch(error => {
            alert(`There was a problem downloading the document: ${error}`);
        });
}

function clearProcessedFile() {
    const endpoint = '/api/v1/generate/clear'
    const options = {
        method: 'GET'
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            alert("Successfully cleared the processed file");
        })
        .catch(error => {
            alert(`There was a problem cleaning the processed job: ${error}`);
        });
}

/*
Task from the backend:
{
    "task_name": self.name, #action items, summary
    "processing": self.is_processing,
    "state" : self.state, #ready, processing, evalluation, finished
    "transcript": self.transcript,  
    "processed_filename": self.processed_filename #transcript filename
}
*/

function toggleProcessingJob(transcriptName, taskName, progress) {
    const div = document.createElement("div");
    div.innerHTML = getProcessingJobStatusComponent(transcriptName, taskName, progress);
    document.getElementById("jobStatusContainer").appendChild(div);
}

function toggleNotProcessingJob() {
    document.getElementById("generate").disabled = false;
    const div = document.createElement("div");
    div.innerHTML = getNotProcessingStatusComponent();
    document.getElementById("jobStatusContainer").appendChild(div);
}

function toggleProcessedJob(transcriptName, taskName, processed_filename) {
    document.getElementById("generate").disabled = false;
    const div = document.createElement("div");
    div.innerHTML = getProcessedStatusComponent(taskName, transcriptName, processed_filename);
    document.getElementById("jobStatusContainer").appendChild(div);
}

function generateSummary() {
    const transcript = document.getElementById("transcriptList").value;
    //var chunkSize = parseInt(document.getElementById("chunk_size").value) || 400;
    var chunkSize = 400;
    const summarizationLanguage = document.getElementById("language").value;
    const enableEvalluationSystem = false;
    //const enableEvalluationSystem = document.getElementById("evalluation").value;

    chunkSize = chunkSize > 2000 ? 2000 : chunkSize;

    body = JSON.stringify({
        transcript,
        chunkSize,
        summarizationLanguage,
        enableEvalluationSystem
    })

    const endpoint = '/api/v1/generate/summary'

    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: body
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            alert("Successfully triggered the job");
        })
        .catch(error => {
            alert(`There was a problem when triggering the job: ${error}`);
        });
    
}

function generateCustomRequestFromTranscript() {
    const transcript = document.getElementById("transcriptList").value;
    //var chunkSize = parseInt(document.getElementById("chunk_size").value) || 400;
    var chunkSize = 400;
    const language = document.getElementById("language").value;
    const userRequest = document.getElementById("userRequest").value;

    chunkSize = chunkSize > 2000 ? 2000 : chunkSize;

    body = JSON.stringify({
        transcript,
        chunkSize,
        language,
        userRequest
    })

    const endpoint = '/api/v1/generate/custom'

    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: body
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            alert("Successfully triggered the job");
        })
        .catch(error => {
            alert(`There was a problem when triggering the job: ${error}`);
        });
}


function generateActionItems() {
    const transcript = document.getElementById("transcriptList").value;
    //var chunkSize = parseInt(document.getElementById("chunk_size").value) || 400;
    var chunkSize = 400;
    const language = document.getElementById("language").value;
    const participants = document.getElementById("participants").value;

    chunkSize = chunkSize > 2000 ? 2000 : chunkSize;

    body = JSON.stringify({
        transcript,
        chunkSize,
        language,
        participants
    })

    const endpoint = '/api/v1/generate/action-items'

    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: body
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            alert("Successfully triggered the job");
        })
        .catch(error => {
            alert(`There was a problem when triggering the job: ${error}`);
        });
}

function generateMeetingMinutes() {
    const transcript = document.getElementById("transcriptList").value;
    //var chunkSize = parseInt(document.getElementById("chunk_size").value) || 400;
    var chunkSize = 400;
    const language = document.getElementById("language").value;
    const participants = document.getElementById("participants").value;
    console.log(participants);

    chunkSize = chunkSize > 2000 ? 2000 : chunkSize;

    body = JSON.stringify({
        transcript,
        chunkSize,
        language,
        participants
    })

    const endpoint = '/api/v1/generate/minutes'

    const options = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: body
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            alert("Successfully triggered the job");
        })
        .catch(error => {
            alert(`There was a problem when triggering the job: ${error}`);
        });
}