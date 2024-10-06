let progressValue = 0;
const BACKEND_URL = "http://localhost:8000"

window.onload = function fillParameters() {
    fillAvailableModels();
    fillAvailableTranscriptions();
}

function fillAvailableModels() {
    let endpoint = "/api/models";

    const options = {
        method: 'GET',
        Authorization: 'EXAMPLE',
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
                document.getElementById("modelSelection").appendChild(newOption);
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}


function fillAvailableTranscriptions() {
    let endpoint = "/api/transcription_files";

    const options = {
        method: 'GET',
        Authorization: 'EXAMPLE',
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
                document.getElementById("transcriptionSelection").appendChild(newOption);
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}


function updateProgress() {
    if (progressValue < 100) {
        progressValue += 10;
        const progressBar = document.getElementById('progressBar');
        progressBar.style.width = progressValue + '%';
        progressBar.setAttribute('aria-valuenow', progressValue);
        progressBar.innerText = progressValue + '%';
    }
}

async function getSelectedOutputType() {
    const radioButtons = document.getElementsByName('radio');

    for (const radioButton of radioButtons) {
        if (radioButton.checked) {
            return radioButton.value;
        }
    }
}

document.getElementById("generateResponse").onclick = async function() {
    const modelSelected = document.getElementById('modelSelection').value;
    const transcriptionFile = document.getElementById('transcriptionSelection').value;
    const temperature = document.getElementById('tempInput').value || document.getElementById('tempInput').placeholder;
    const topP = document.getElementById('topPInput').value || document.getElementById('topPInput').placeholder;
    const modelConfiguration =  {temperature, topP}
    const outputType = await getSelectedOutputType();

    data = {modelSelected, modelConfiguration, outputType, transcriptionFile}
    endpoint = "/api/send"
    console.log(data)

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        Authorization: 'EXAMPLE',
        body: JSON.stringify(data),
    };

    fetch(BACKEND_URL + endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(responseData => {
            console.log('Response from backend:', responseData);
            alert('Data posted successfully: ' + JSON.stringify(responseData));
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

document.getElementById("confirmFileUpload").onclick = async function() {
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);
    const options = {
        method: 'POST',
        body: formData,
        'Content-Type': "text/html; charset=utf-8"
    }
    await fetch(BACKEND_URL + "/api/upload/transcription_file", options)
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        $('#uploadModal').modal('hide');
        fillAvailableTranscriptions();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
    

}