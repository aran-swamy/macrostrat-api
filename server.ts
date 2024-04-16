var express = require("express"),
  bodyParser = require("body-parser"),
  //v1 = require("./v1"),
  v2 = require("./v2test"),
  defs = require("./v2test/defs"),
  app = express();

var ua = require("universal-analytics");

ua(
  "UA-75785431-1",
  null,
  {},
  {
    dh: "https://macrostrat.org/api",
  },
);

app.use(function (req, res, next) {
  // Ignore requests from the status server
  if (req.query && req.query.skip) {
    return next();
  }

  var ip = req.headers["x-forwarded-for"] || req.connection.remoteAddress;
  var visitor = ua("UA-75785431-1", { https: true });

  visitor
    .pageview({
      dp: req.originalUrl,
      uip: ip || "0.0.0.0",
      an: req.query && req.query.referrer ? req.query.referrer : "",
      av: req.query && req.query.version ? req.query.version : "",
    })
    .send();
  next();
});

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));

// parse application/json
app.use(bodyParser.json());

// parse application/vnd.api+json as json
app.use(bodyParser.json({ type: "application/vnd.api+json" }));

// Load and prefix all routes with /api and appropriate version
app.use("/v2", v2);

// If no version specified, fall back to more current
app.use("/", v2);

app.set("json spaces", 2);

app.port = process.argv[2] || 5550;

app.start = function () {
  app.listen(app.port, function () {
    console.log("Listening on port " + app.port);
  });
};

if (!module.parent) {
  app.start();
}

//module.exports = app;
export { app };
