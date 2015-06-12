var api = require("../api"),
    larkin = require("../larkin");

module.exports = function(req, res, next, cb) {
  if (Object.keys(req.query).length < 1) {
    return larkin.info(req, res, next);
  }

  var where = [],
      params = {};

  

  if (req.query.rule) {
    if (req.query.rule === "down") {
      if (req.query.strat_name) {
        where.push("parent = (SELECT strat_name_id FROM lookup_strat_names WHERE strat_name = :strat_name) OR strat_name_id = (SELECT strat_name_id FROM lookup_strat_names WHERE strat_name = :strat_name)");
        params["strat_name"] = req.query.strat_name;

      } else if (req.query.strat_name_id) {
        where.push("parent IN (:strat_name_id) OR strat_name_id IN (:strat_name_id)");
        params["strat_name_id"] = larkin.parseMultipleIds(req.query.strat_name_id);
      }
      
    } else if (req.query.rule === "all") {
      if (req.query.strat_name) {
        where.push("tree = (SELECT tree FROM lookup_strat_names WHERE strat_name = :strat_name)");
        params["strat_name"] = req.query.strat_name;

      } else if (req.query.strat_name_id) {
        where.push("tree = (SELECT tree FROM lookup_strat_names WHERE strat_name_id IN (:strat_name_id))");
        params["strat_name_id"] = larkin.parseMultipleIds(req.query.strat_name_id);
      }
    }
  } else {
    if (req.query.strat_name_id) {
      where.push("strat_name_id IN (:strat_name_id)");
      params["strat_name_id"] = larkin.parseMultipleIds(req.query.strat_name_id);

    } else if (req.query.strat_name_like) {
      where.push("lower(strat_name) LIKE lower(:strat_name)");
      params["strat_name"] = req.query.strat_name_like + "%";

    } else if (req.query.strat_name) {
      where.push("lower(strat_name) LIKE lower(:strat_name)");
      params["strat_name"] = req.query.strat_name;
    } 

    if (req.query.rank) {
      where.push("rank = :rank");
      params["rank"] = req.query.rank;
    }

  }

  var sql = "SELECT strat_name, rank, strat_name_id, bed_name bed,bed_id, mbr_name mbr, mbr_id, fm_name fm, fm_id, gp_name gp, gp_id, sgp_name sgp, sgp_id, early_age AS b_age, late_age AS t_age, gsc_lexicon FROM lookup_strat_names";

  if (where.length > 0) {
    sql += " WHERE " + where.join(" AND ")
  }

  if ("sample" in req.query) {
    sql += " LIMIT 5";
  }
  
  larkin.query(sql, params, function(error, response) {
    if (error) {
      console.log(error);
      if (cb) {
        cb(error);
      } else {
        larkin.error(req, res, next, "Something went wrong");
      }
      
    } else {
      if (cb) {
        cb(null, response);
      } else {
        larkin.sendData(response, res, (api.acceptedFormats.standard[req.query.format]) ? req.query.format : "json", next);
      }
    }
  });
}

