var api = require("./api"),
    larkin = require("./larkin");

api.route("/")
  .get(require("./root"));

api.route("/column")
  .get(require("./column"));

api.route("/columns")
  .get(require("./columns"));

api.route("/sections")
  .get(require("./sections"));

api.route("/unit")
  .get(require("./unit"));

api.route("/units")
  .get(require("./units"));

api.route("/fossils")
  .get(require("./fossils"));

api.route("/stats")
  .get(require("./stats"));

api.route("/lith_definitions")
  .get(require("./lith_definitions"));

api.route("/lithatt_definitions")
  .get(require("./lithatt_definitions"));

api.route("/environ_definitions")
  .get(require("./environ_definitions"));

api.route("/interval_definitions")
  .get(require("./interval_definitions"));

api.route("/strat_names")
  .get(require("./strat_names"));

api.route("/section_stats")
  .get(require("./section_stats"));

api.route("/paleogeography")
  .get(require("./paleogeography"));

api.route("/geologic_units")
  .get(require("./geologic_units"));

api.route("/geologic_units/intersection")
  .get(require("./geologic_units_intersection"));

api.route("/geologic_units/map")
  .get(require("./geologic_units_map"));

api.route("/mobile/point")
  .get(require("./mobile_point"));

api.route("/mobile/point_details")
  .get(require("./mobile_point_details"));

api.route("/mobile/fossil_collections")
  .get(require("./mobile_fossil_collections"));

api.route("/editing/map")
  .get(require("./editing_map"));

api.route("/editing/map/update")
  .post(require("./editing_map_update"));

api.route("/editing/section")
  .get(require("./editing_section"));

api.route("/editing/units/update")
  .put(require("./editing_units_update"));

api.route("*")
  .get(require("./catchall"));

api.use(function(err, req, res, next) {
  if(err.status !== 404) {
    return next();
  } else if (err.status === 404) {
    larkin.error(req, res, next, "404: Page not found", 404);
  } else {
    larkin.error(req, res, next, "500: Internal Server Error", 500);
  }
});

module.exports = api;
