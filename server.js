var express = require("express"),
    bodyParser = require("body-parser"),
    v1 = require("./v1"),
    v2 = require("./v2"),
    app = express();

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }))

// parse application/json
app.use(bodyParser.json())

// parse application/vnd.api+json as json
app.use(bodyParser.json({ type: "application/vnd.api+json" }))

// Load and prefix all routes with /api and appropriate version
app.use("/api/v1", v1);
app.use("/api/v2", v2);

// If no version specified, fall back to more current
app.use("/api", v2);

app.set("json spaces", 2);

app.port = process.argv[2] || 5000;

app.start = function() {
  app.listen(app.port, function() {
    console.log("Listening on port " + app.port);
  });
}

if (!module.parent) {
  app.start();
}


module.exports = app;
