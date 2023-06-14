const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path'); // import the path module
const ObjectId = require('mongoose').Types.ObjectId;
const fs = require('fs');
const https = require('https');

const app = express();
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

// Serve static files from the React app
app.use(express.static(path.join(__dirname, '../ui')));

// SSL Certificate
const privateKey = fs.readFileSync(path.join(__dirname, 'key.pem'), 'utf8');
const certificate = fs.readFileSync(path.join(__dirname, 'cert.pem'), 'utf8');

const credentials = {
  key: privateKey,
  cert: certificate,
  passphrase: 'admin'  // replace with your private key password
};

// Starting both http & https servers
const httpsServer = https.createServer(credentials, app);

httpsServer.listen(3000, () => {
    console.log('HTTPS Server running on port 3000');
});



// Mongoose connection
mongoose.connect('mongodb://localhost:27017/newsfeeds', { useNewUrlParser: true, useUnifiedTopology: true });

const ActionSchema = new mongoose.Schema({}, { strict: false, _id: false });

// Mongoose schema for newsfeed items
const NewsFeedItemSchema = new mongoose.Schema({
  _id:  mongoose.Schema.Types.ObjectId,
  title: String,
  link: String,
  text: String,
  date: Date,
  scores: [{ attribute: String, score: Number }],
  actions: [ActionSchema],
});

// Mongoose model for newsfeed items
const NewsFeedItem = mongoose.model('NewsFeedItem', NewsFeedItemSchema, 'feeditems');

// API endpoint to get newsfeed items
app.get('/api/newsfeeds', async (req, res) => {
  try {
    const newsfeedItems = await NewsFeedItem.find({ });
    res.json(newsfeedItems);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// API endpoint to perform an action on a newsfeed item
app.post('/api/newsfeeds/:_id/do_action', async (req, res) => {
  try {
    const { action, value } = req.body;
    await NewsFeedItem.updateOne({ _id: req.params._id }, { $push: { actions: { action, value } } });
    res.json({ message: 'Action performed successfully' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});


// API endpoint to perform an action on multiple newsfeed items
app.post('/api/newsfeeds/do_action', async (req, res) => {
  try {
    const updates = req.body;
    let result = [];
    for (let update of updates) {
      const { _id, actions } = update;
      console.log(actions);	
      const updateResult = await NewsFeedItem.updateOne({_id: new ObjectId(update._id) }, { $push: { actions:actions } });
      result.push(updateResult);
     console.log(updateResult, {_id, actions});
    }
    res.json({ message: 'Actions performed successfully', result });
  } catch (err) {
     console.log("err",err);
    res.status(500).json({ message: err.message });
  }
});

