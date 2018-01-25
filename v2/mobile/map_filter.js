'use strict'

const larkin = require('../larkin')

module.exports = (req, res, next) => {
  const validFilters = [
    'lith_class',
    'lith_type',
    'lith',
    'lith_id'
  ]

  let where = []
  let params = []
  if (req.query.lith_class) {
    where.push(`lith_classes && $${where.length + 1}`)
    params.push(req.query.lith_class.split(','))
  }
  if (req.query.lith_type) {
    where.push(`lith_types && $${where.length + 1}`)
    params.push(req.query.lith_type.split(','))
  }

  let sql = `
    SELECT map_id
    FROM lookup_large
    WHERE ${where.join(' AND ')}
    UNION ALL
    SELECT map_id
    FROM lookup_medium
    WHERE ${where.join(' AND ')}
    UNION ALL
    SELECT map_id
    FROM lookup_small
    WHERE ${where.join(' AND ')}
    UNION ALL
    SELECT map_id
    FROM lookup_tiny
    WHERE ${where.join(' AND ')}
  `
  larkin.queryPg('burwell', sql, params, (error, result) => {
    if (error) return larkin.error(req, res, next)
    res.json(result.rows.map(row => { return row.map_id }))
  })
}
