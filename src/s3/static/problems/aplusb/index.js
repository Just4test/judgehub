const express = require('express')
const request = require('request')
const bodyParser = require('body-parser')
const fs = require('fs')
const app = express()

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

app.get('/get_modes', function (req, res) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Content-Length, Authorization, Accept, X-Requested-With , yourHeaderFeild');
  res.header('Access-Control-Allow-Methods', 'PUT, POST, GET, DELETE, OPTIONS');

  var data = fs.readFile("./lang.json", "utf-8", function (err, data) {
    var jsonData = JSON.parse(data);
    var arr = [];
    for (var i = 0, len = jsonData.length; i < len; i++) {
      var obj = {};
      obj.lang = jsonData[i].lang;
      obj.modeId = jsonData[i].modeId;
      var code = fs.readFileSync(jsonData[i].sampleUrl, "utf-8");
      if (code) {
        obj.sampleCode = code;
      } else {
        obj.sampleCode = "";
      }
      arr.push(obj)
    }
    res.send(JSON.stringify(arr));
  });

})

app.post('/get_code_result', function (req, res) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Content-Length, Authorization, Accept, X-Requested-With , yourHeaderFeild');
  res.header('Access-Control-Allow-Methods', 'PUT, POST, GET, DELETE, OPTIONS');

  var url = 'https://rb8z5mwjp4.execute-api.us-east-1.amazonaws.com/Prod/submit';

  var options = {
    url: url,
    method: 'POST',
    json: true,
    headers: {
      'Content-Type': 'application/json; charset=UTF-8'
    },
    body: req.body,
    // proxy: 'http://10.4.70.103:8888'
  }

  request(options, function(error, response, body){

		try{
      // console.log(response.body);
			if (response.statusCode == 200 || response.statusCode == 304) {
        res.status(200).send(response.body);
			} else {
        res.status(400).send({error: '获取失败'});
      }
		}catch(error){
			//TODO handle the exception
      console.log("error:"+ error);
      res.status(400).send({status: 0, error: error});
		}
  })

});

var server = app.listen(3333, '127.0.0.1', function () {
  var host = server.address().address;
  var port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});
