var api = require("./api"),
    larkin = require("./larkin"),
    multiline = require("multiline");

module.exports = function(req, res, next) {
  if (Object.keys(req.query).length < 1) {
    return larkin.info(req, res, next);
  }

  var sql = multiline(function() {/*
    SELECT project_id, project, status_code status, COUNT(distinct units_sections.col_id) AS columns, COUNT(distinct units_sections.section_id) AS packages, COUNT(distinct unit_id) AS units, COUNT(distinct collection_no) AS pbdb_collections, COUNT(unit_measures.id) AS measurements
    FROM units_sections
    JOIN cols ON cols.id = col_id
    JOIN projects ON projects.id = project_id
    LEFT JOIN pbdb_matches USING (unit_id)
    LEFT JOIN unit_measures USING (unit_id)
    WHERE project IN ('North America','New Zealand','Caribbean','Deep Sea') and status_code='active'
    GROUP BY project_id, status_code;
  */});


  var format = (api.acceptedFormats.standard[req.query.format]) ? req.query.format : "json";

  larkin.query(sql, [], null, true, res, format, next);
}
