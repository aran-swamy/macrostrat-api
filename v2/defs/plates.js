var api = require("../api"),
    larkin = require("../larkin");

module.exports = function(req, res, next) {
  if (Object.keys(req.query).length < 1) {
    return larkin.info(req, res, next);
  }

  var sql = "SELECT plateid AS plate_id, names AS name FROM name_lookup",
      params = [];

  if (req.query.plate_id) {
    sql += " WHERE plateid = ANY($1)";
    params.push(larkin.parseMultipleIds(req.query.plate_id));
  }

  if ("sample" in req.query) {
    sql += " LIMIT 5";
  }

  larkin.queryPg("alice", sql, params, function(error, result) {
    if (error) {
      larkin.error(req, res, next, error);
    } else {
      larkin.sendCompact(result.rows, res, (api.acceptedFormats.standard[req.query.format]) ? req.query.format : "json", next);
    }
  });
}