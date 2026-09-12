const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = express();
const port = 3000;

app.use(express.static(__dirname));

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, 'uploads'));
  },
  filename: (req, file, cb) => {
    cb(null, 'test.jpg');
  },
});

const upload = multer({ storage: storage });

app.use(express.static('public'));

app.post('/upload', upload.single('image'), (req, res) => {
  res.send('Image uploaded successfully.');
});

app.post('/process', (req, res) => {
  exec(`python loc.py`, { cwd: path.join(__dirname, 'Kavin') }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing loc.py: ${error.message}`);
      return res.status(500).send('Error processing loc.py');
    }

    exec('python ./app.py', (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing app.py: ${error.message}`);
        return res.status(500).send('Error processing app.py');
      }
      console.log(`${stdout}`);
      res.send('Image processed successfully.');
    });
  });
});

app.get('/overlay', (req, res) => {
  res.sendFile(path.join(__dirname, 'overlay.png'));
});

app.get('/result', (req, res) => {
  const file1 = './result.txt';
  const file2 = './Kavin/coordinates.txt';

  fs.readFile(file1, 'utf8', (err1, data1) => {
    if (err1) {
      console.error(`Error reading ${file1}:`, err1);
      return res.status(500).send(`Error reading ${file1}`);
    }

    fs.readFile(file2, 'utf8', (err2, data2) => {
      if (err2) {
        console.error(`Error reading ${file2}:`, err2);
        return res.status(500).send(`Error reading ${file2}`);
      }

      res.send(`${data1}\n${data2}`);
    });
  });
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
