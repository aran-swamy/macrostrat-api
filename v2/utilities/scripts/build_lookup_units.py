import MySQLdb
import MySQLdb.cursors
from warnings import filterwarnings
import sys
from credentials import *

# Connect to Macrostrat
try:
  connection = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db, unix_socket=mysql_unix_socket, cursorclass=MySQLdb.cursors.DictCursor)
except:
  print "Could not connect to database: ", sys.exc_info()[1]
  sys.exit()

# Cursor for MySQL
cursor = connection.cursor()

# Ignore warnings
filterwarnings('ignore', category = MySQLdb.Warning)

def get_time(qtype, params) :
    params["type"] = qtype
    cursor.execute("""
        SELECT interval_name, intervals.id from intervals
        JOIN timescales_intervals ON intervals.id = interval_id
        JOIN timescales on timescale_id = timescales.id
        WHERE timescale = %(type)s
            AND %(b_age)s > age_top
            AND %(b_age)s <= age_bottom
            AND %(t_age)s < age_bottom
            AND %(t_age)s >= age_top
    """, params)
    data = cursor.fetchone()

    if data is not None:
        return {
            "name": data["interval_name"],
            "id": data["id"]
        }
    else :
        return {
            "name": "",
            "id": ""
        }

# Copy structure into new table
cursor.execute("""
    DROP TABLE IF EXISTS lookup_units_new;
    CREATE TABLE lookup_units_new LIKE lookup_units;
""")
cursor.close()
cursor = connection.cursor()

# Initial query to populate the lookup table
cursor.execute("""
    INSERT INTO lookup_units_new (unit_id, col_area, project_id, t_int, t_int_name, t_int_age, t_age, t_prop, t_plat, t_plng, b_int, b_int_name, b_int_age, b_age, b_prop, b_plat, b_plng, clat,  clng, color, text_color, units_above, units_below, pbdb_collections)
    SELECT
      units.id AS unit_id,
      cols.col_area,
      cols.project_id,
      t_int,
      tint.interval_name AS t_int_name,
      tint.age_top AS t_int_age,
      t_age,
      t_prop,
      IFNULL(t_plat, '') AS t_plat,
      IFNULL(t_plng, '') AS t_plng,
      b_int,
      bint.interval_name AS b_int_name,
      bint.age_bottom AS b_int_age,
      b_age,
      b_prop,
      IFNULL(b_plat, '') AS b_plat,
      IFNULL(b_plng, '') AS b_plng,
      cols.lat AS clat,
      cols.lng AS clng,
      colors.unit_hex AS color,
      colors.text_hex AS text_color,
      GROUP_CONCAT(distinct ubt.unit_id_2 SEPARATOR '|') AS units_above,
      GROUP_CONCAT(distinct ubb.unit_id SEPARATOR '|') AS units_below,
      COUNT(DISTINCT collection_no) AS pbdb_collections
    FROM (
      SELECT
          units.id,
          (
            SELECT t1
            FROM unit_boundaries
            WHERE unit_id = units.id
            ORDER BY t1_age asc
            LIMIT 1
          ) t_int,
          (
            SELECT t1_age
            FROM unit_boundaries
            WHERE unit_id = units.id
            ORDER BY t1_age asc
            LIMIT 1
          ) t_age,
          (
            SELECT t1_prop
            FROM unit_boundaries
            WHERE unit_id = units.id
            ORDER BY t1_age asc
            LIMIT 1
          ) t_prop,
          (
            SELECT paleo_lat
            FROM unit_boundaries
            WHERE unit_id = units.id
            ORDER BY t1_age asc
            LIMIT 1
          ) t_plat,
          (
            SELECT paleo_lng
            FROM unit_boundaries
            WHERE unit_id = units.id
            ORDER BY t1_age asc
            LIMIT 1
          ) t_plng,
          (
            SELECT t1
            FROM unit_boundaries
            WHERE unit_id_2 = units.id
            ORDER BY t1_age desc
            LIMIT 1
          ) b_int,
          (
            SELECT t1_age
            FROM unit_boundaries
            WHERE unit_id_2 = units.id
            ORDER BY t1_age desc
            LIMIT 1
          ) b_age,
          (
            SELECT t1_prop
            FROM unit_boundaries
            WHERE unit_id_2 = units.id
            ORDER BY t1_age desc
            LIMIT 1
          ) b_prop,
          (
            SELECT paleo_lat
            FROM unit_boundaries
            WHERE unit_id_2 = units.id
            ORDER BY t1_age desc
            LIMIT 1
          ) b_plat,
          (
            SELECT paleo_lng
            FROM unit_boundaries
            WHERE unit_id_2 = units.id
            ORDER BY t1_age desc
            LIMIT 1
          ) b_plng,
          units.color,
          units.col_id
      FROM units
      GROUP BY units.id
    ) units
    LEFT JOIN intervals tint ON tint.id = units.t_int
    LEFT JOIN intervals bint ON bint.id = units.b_int
    LEFT JOIN colors ON units.color = colors.color
    LEFT JOIN pbdb_matches ON pbdb_matches.unit_id = units.id
    LEFT JOIN cols ON cols.id = units.col_id
    LEFT JOIN unit_boundaries ubb ON ubb.unit_id_2 = units.id
    LEFT JOIN unit_boundaries ubt ON ubt.unit_id = units.id
    GROUP BY units.id
""")
cursor.close()
cursor = connection.cursor()

# Gather basic info about all units just inserted so that we can loop through them
cursor.execute("""
    SELECT unit_id, t_age, t_int, t_prop, b_age, b_int, b_prop FROM lookup_units_new
""")
units = cursor.fetchall()

for idx, unit in enumerate(units):
    # Give some feedback
    sys.stdout.write("%s of %s  \r" % (idx, len(units)) )
    sys.stdout.flush()

    # Used to get times
    params = {
        "t_age": unit["t_age"],
        "b_age": unit["b_age"]
    }

    # Get age
    age = get_time("international ages", params)

    # Get epoch
    epoch = get_time("international epochs", params)

    # Get period
    period = get_time("international periods", params)

    # Get era
    era = get_time("international eras", params)

    # Get eon
    eon = get_time("international eons", params)

    # Update the lookup table with detailed time info
    cursor.execute("""
        UPDATE lookup_units_new SET
            age = %(age)s,
            age_id = %(age_id)s,
            epoch = %(epoch)s,
            epoch_id = %(epoch_id)s,
            period = %(period)s,
            period_id = %(period_id)s,
            era = %(era)s,
            era_id = %(era_id)s,
            eon = %(eon)s,
            eon_id = %(eon_id)s
        WHERE unit_id = %(unit_id)s
    """, {
        "age": age["name"],
        "age_id": age["id"],
        "epoch": epoch["name"],
        "epoch_id": epoch["id"],
        "period": period["name"],
        "period_id": period["id"],
        "era": era["name"],
        "era_id": era["id"],
        "eon": eon["name"],
        "eon_id": eon["id"],
        "unit_id": unit["unit_id"]
    })

    # Check if t_prop == 1, and if so get the next oldest interval of the same scale
    if unit["t_prop"] == 1 :
        cursor.execute("""
            SELECT intervals.interval_name, intervals.id, intervals.age_top
            FROM intervals
            JOIN timescales_intervals ON intervals.id = timescales_intervals.interval_id
            WHERE timescales_intervals.timescale_id IN (
                SELECT timescale_id FROM timescales_intervals WHERE interval_id = %(int_id)s
            ) AND age_top = (
                SELECT age_bottom FROM intervals WHERE id = %(int_id)s
            )
        """, {"int_id": unit["t_int"]})
        data = cursor.fetchone()

        if data is not None:
            print "Should update top interval ", unit["unit_id"]
            cursor.execute("""
                UPDATE lookup_units_new SET
                    t_int = %(t_int)s,
                    t_int_name = %(t_int_name)s,
                    t_int_age = %(t_int_age)s
                WHERE unit_id = %(unit_id)s
            """, {
                "t_int": data["id"],
                "t_int_name": data["interval_name"],
                "t_int_age": data["age_top"],
                "unit_id": unit["unit_id"]
            })


    # Check if b_prop == 1, if so get the next youngest time interval
    if unit["b_prop"] == 1 :
        cursor.execute("""
            SELECT intervals.interval_name, intervals.id, intervals.age_bottom
            FROM intervals
            JOIN timescales_intervals ON intervals.id = timescales_intervals.interval_id
            WHERE timescales_intervals.timescale_id IN (
                SELECT timescale_id FROM timescales_intervals WHERE interval_id = %(int_id)s
            ) AND age_bottom = (
                SELECT age_top FROM intervals WHERE id = %(int_id)s
            )
        """, {"int_id": unit["t_int"]})
        data = cursor.fetchone()

        if data is not None:
            print "Should update bottom interval ", unit["unit_id"]
            cursor.execute("""
                UPDATE lookup_units_new SET
                    b_int = %(b_int)s,
                    b_int_name = %(b_int_name)s,
                    b_int_age = %(b_int_age)s
                WHERE unit_id = %(unit_id)s
            """, {
                "b_int": data["id"],
                "b_int_name": data["interval_name"],
                "b_int_age": data["age_bottom"],
                "unit_id": unit["unit_id"]
            })


# Modify results for long-ranging units
cursor.execute("""
    UPDATE lookup_units_new SET
        period = eon
    WHERE period = '' AND eon = 'Archean';

    UPDATE lookup_units_new SET
        period = 'Precambrian'
    WHERE period = '' AND t_age >= 541;
""")
cursor.close()
cursor = connection.cursor()

# Clean up
cursor.execute("""
    TRUNCATE TABLE lookup_units;
    INSERT INTO lookup_units SELECT * FROM lookup_units_new;
    DROP TABLE lookup_units_new;
""")
cursor.close()
cursor = connection.cursor()


# Validate results
cursor.execute("""
    SELECT COUNT(*) N, (SELECT COUNT(*) FROM lookup_units) nn FROM units
""")
data = cursor.fetchone()

if data['N'] != data['nn'] :
    print "ERROR: inconsistent unit count in lookup_unit_intervals_new table. ", data['nn'], " datas in `lookup_units` and ", data['N'], " datas in `units`."
    sys.exit()

'''
#modifiy results for long-ranging units
cursor.execute("UPDATE lookup_unit_intervals_new set period = concat_WS('-',FO_period,LO_period) where period = '' and FO_period not like ''")

cursor.execute("UPDATE lookup_unit_intervals_new set period = concat_WS('-', FO_interval, LO_period) where FO_interval = 'Archean'")
'''

print "Done with lookup_units"
