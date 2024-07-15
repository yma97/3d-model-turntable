const express = require('express');
const fileUpload = require('express-fileupload');
const path = require('path');
const { exec } = require('child_process');
const Queue = require('bull');
const redis = require('redis');

// Create a new queue
const renderQueue = new Queue('renderQueue', {
  redis: {
    host: '127.0.0.1',
    port: 6379
  }
});

const app = express();

app.use(fileUpload());
app.use(express.static(path.join(__dirname)));

// Serve the HTML file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Handle file uploads
app.post('/upload', async (req, res) => {
  if (!req.files || Object.keys(req.files).length === 0) {
    return res.status(400).send('No files were uploaded.');
  }

  const modelFile = req.files.modelFile;
  const uploadPath = path.join(__dirname, 'uploads', modelFile.name);

  try {
    await modelFile.mv(uploadPath);
    const job = await renderQueue.add({
      uploadPath: uploadPath,
      outputFileName: `${path.parse(modelFile.name).name}.mp4`
    });

    res.send({ success: true, jobId: job.id });
  } catch (err) {
    res.status(500).send(err);
  }
});

// Handle job progress
app.get('/job/:id', async (req, res) => {
  const job = await renderQueue.getJob(req.params.id);
  if (job === null) {
    return res.status(404).send({ error: 'Job not found' });
  }
  const progress = job.progress();
  res.send({ progress });
});

// Serve static files
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/videos', express.static(path.join(__dirname, 'videos')));

// Process jobs
renderQueue.process(async (job, done) => {
  const { uploadPath, outputFileName } = job.data;
  const outputVideoPath = path.join(__dirname, 'videos', outputFileName);
  const blenderPath = '/Applications/Blender.app/Contents/MacOS/Blender'; // Ensure this path is correct
  const blenderCommand = `${blenderPath} -b -P render_turntable.py -- ${uploadPath} ${outputVideoPath}`;

  exec(blenderCommand, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      done(new Error('Blender render failed'));
    } else {
      done(null, { outputVideoPath });
    }
  });
});

renderQueue.on('completed', (job, result) => {
  console.log(`Job completed with result: ${result.outputVideoPath}`);
});

renderQueue.on('failed', (job, err) => {
  console.log(`Job failed with error: ${err.message}`);
});

app.listen(3000, () => {
  console.log('Server started on http://localhost:3000');
});

