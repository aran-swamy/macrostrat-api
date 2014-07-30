var mysql = require("mysql"),
    pg = require("pg"),
    async = require("async"),
    winston = require("winston"),
    credentials = require("./routes/credentials"),
    csv = require('express-csv');


winston.add(winston.transports.File, { filename: "logs/larkin.log" });

(function() {
  var larkin = {};

  larkin.connectMySQL = function() {
    this.connection = mysql.createConnection(credentials.mysql);

    this.connection.connect(function(error) {
      if (error) {
        this.log("error", error);
      } else {
        this.log("info", "Connected to MySQL");
      }
    }.bind(this));

    this.connection.on("error", function(err) {
      this.log("error", err);
      this.connectMySQL();
    }.bind(this));
  };

  larkin.queryPg = function(sql, params, callback, send, res, format, next) {
    pg.connect("postgres://" + credentials.pg.user + "@" + credentials.pg.host + "/" + credentials.pg.database, function(err, client, done) {
      if (err) {
        this.log("error", error);
      }
      client.query(sql, params, function(err, result) {
        done();

        if (err) {
          this.log("error", err);
        }

        if (send) {
          this.sendData(result, res, format, next);
        } else {
          callback(result);
        }
      }.bind(this));
    }.bind(this));
  }

  larkin.query = function(sql, params, callback, send, res, format, next) {
    this.connection.query(sql, params, function(error, result) {
      if (error) {
        this.error(res, next, "Error retrieving from MySQL.", error);
      } else {
        if (send) {
          this.sendData(result, res, format, next);
        } else {
          callback(result);
        }
      }
    }.bind(this));
  };

  larkin.sendData = function(data, res, format, next) {
    if (format === "csv") {
      res.csv(data, true)
    } else {
      res.json({
        "success": {
        "results": data.length,
        "data": data
        }
      });
    }
   };


  larkin.error = function(res, next, message, options, code) {
    this.log("error", message);
    res.json((code) ? code : 200, {
      "error": {
        "message": message,
        "options": options
      }
    });
  };

  larkin.log = function(type, message) {
    winston.log(type, message);
  }

  module.exports = larkin;

}());