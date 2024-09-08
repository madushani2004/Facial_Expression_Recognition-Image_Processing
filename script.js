function toggleProcessingButtons() {
    const buttonsSection = document.getElementById('buttons-section');
    if (buttonsSection.style.display === 'none') {
        buttonsSection.style.display = 'flex';
    } else {
        buttonsSection.style.display = 'none';
    }
}

function handleUpload() {
    const upload = document.getElementById('upload').files[0];
    if (!upload) {
        alert('Please select an image file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', upload);

    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('image').src = 'data:image/jpeg;base64,' + data.image;
        document.getElementById('expression').textContent = 'Detected Expression: ' + data.expression;
        document.getElementById('result').style.display = 'block';
    })
    .catch(error => console.error('Error uploading file:', error));
}

function processImage(action) {
    const upload = document.getElementById('upload').files[0];
    if (!upload) {
        alert('Please select an image file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', upload);
    formData.append('action', action);

    if (action === 'rotate') {
        const angle = prompt('Enter rotation angle:');
        formData.append('angle', angle);
    }

    fetch(`http://localhost:5000/process`, {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output').src = 'data:image/jpeg;base64,' + data.image;
    })
    .catch(error => console.error('Error processing image:', error));
}

document.getElementById('upload').addEventListener('change', function() {
    const img = this.files[0];
    if (img) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('inp').src = e.target.result;
            document.getElementById('result').style.display = 'none';
        };
        reader.readAsDataURL(img);
    }
});
