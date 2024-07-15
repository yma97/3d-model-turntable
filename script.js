document.getElementById('uploadForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const fileInput = document.getElementById('modelFile');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('modelFile', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            checkProgress(data.jobId);
        } else {
            alert('Upload failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Upload failed');
    });
});

function checkProgress(jobId) {
    const interval = setInterval(() => {
        fetch(`/job/${jobId}`)
        .then(response => response.json())
        .then(data => {
            if (data.progress !== undefined) {
                document.getElementById('progressBar').value = data.progress;
            }

            if (data.progress === 100) {
                clearInterval(interval);
                fetch(`/job/${jobId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.progress === 100) {
                        const link = document.createElement('a');
                        link.href = `/videos/${jobId}.mp4`;
                        link.innerText = 'Download Video';
                        link.download = '';
                        document.getElementById('downloadLink').appendChild(link);
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }, 1000);
}

