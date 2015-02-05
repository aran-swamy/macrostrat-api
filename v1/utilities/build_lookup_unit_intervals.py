import MySQLdb
import MySQLdb.cursors
import urllib2
import sys

# Connect to Macrostrat
try:
  connection = MySQLdb.connect(host="", user="", passwd="", db="", unix_socket="/var/tmp/mariadb.sock", cursorclass=MySQLdb.cursors.DictCursor)
except:
  print "Could not connect to database: ", sys.exc_info()[1]
  sys.exit()

# Cursor for MySQL
cursor = connection.cursor()

###############################################################################################
## build lookup_unit_intervals
###############################################################################################
# truncate the table
cursor.execute("TRUNCATE TABLE lookup_unit_intervals")

# initial query
cursor.execute("SELECT units.id,FO,LO, f.age_bottom, f.interval_name fname, f.age_top FATOP, l.age_top, l.interval_name lname, min(u1.t1_age) AS t_age, max(u2.t1_age) AS b_age from units JOIN intervals f on FO=f.id JOIN intervals l ON LO=l.id LEFT JOIN unit_boundaries u1 ON u1.unit_id = units.id LEFT JOIN unit_boundaries u2 ON u2.unit_id_2 = units.id group by units.id")
numrows = cursor.rowcount
row = cursor.fetchall()

# initialize arrays
r2={}
r3={}
r4={}
r5={}
r6={}
rLO={}
rFO={}

#handle each unit
for x in xrange(0,numrows):
	#print row[x]['id']
	
	cursor.execute("SELECT interval_name,intervals.id from intervals JOIN timescales_intervals ON intervals.id=interval_id JOIN timescales on timescale_id=timescales.id WHERE timescale='international epochs' AND %f > age_top AND %f <= age_bottom AND %f < age_bottom AND %f >= age_top" % (row[x]['age_bottom'], row[x]['age_bottom'], row[x]['age_top'], row[x]['age_top']))
	row2=cursor.fetchone()
	if row2 is None:
		r2['interval_name']=''
		r2['id']=0
	else:
		r2['interval_name']=row2['interval_name']
		r2['id']=row2['id']
	
	cursor.execute("SELECT interval_name,intervals.id from intervals JOIN timescales_intervals ON intervals.id=interval_id JOIN timescales on timescale_id=timescales.id WHERE timescale='international periods' AND %f > age_top AND %f <= age_bottom AND %f < age_bottom AND %f >= age_top" % (row[x]['age_bottom'], row[x]['age_bottom'], row[x]['age_top'], row[x]['age_top']))
	row3=cursor.fetchone()
	if row3 is None:
		r3['interval_name']=''
		r3['id']=0
	else:
		r3['interval_name']=row3['interval_name']
		r3['id']=row3['id']

	cursor.execute("SELECT interval_name FROM intervals JOIN timescales_intervals ON intervals.id=interval_id  JOIN timescales on timescale_id=timescales.id WHERE timescale='international periods' and age_bottom>= %f and age_top < %f" % (row[x]['age_bottom'], row[x]['age_bottom']))
	row_period_FO=cursor.fetchone()
	if row_period_FO is None:
		rFO['interval_name']=''
		rFO['id']=0
	else:
		rFO['interval_name']=row_period_FO['interval_name']

	cursor.execute("SELECT interval_name FROM intervals JOIN timescales_intervals ON intervals.id=interval_id  JOIN timescales on timescale_id=timescales.id WHERE timescale='international periods' and age_bottom > %f and age_top <= %f" % (row[x]['age_top'], row[x]['age_top']))
	row_period_LO=cursor.fetchone()
	if row_period_LO is None:
		rLO['interval_name']=''
		rLO['id']=0
	else:
		rLO['interval_name']=row_period_LO['interval_name']

	cursor.execute("SELECT interval_name,intervals.id from intervals JOIN timescales_intervals ON intervals.id=interval_id JOIN timescales on timescale_id=timescales.id WHERE timescale='international ages' AND %f > age_top AND %f <= age_bottom AND %f < age_bottom AND %f >= age_top" % (row[x]['age_bottom'], row[x]['age_bottom'], row[x]['age_top'], row[x]['age_top']))
	row4=cursor.fetchone()
	if row4 is None:
		r4['interval_name']=''
		r4['id']=0
	else:
		r4['interval_name']=row4['interval_name']
		r4['id']=row4['id']

	cursor.execute("SELECT interval_name,intervals.id from intervals WHERE interval_type='eon' AND %f > age_top AND %f <= age_bottom AND %f < age_bottom AND %f >= age_top" % (row[x]['age_bottom'], row[x]['age_bottom'], row[x]['age_top'], row[x]['age_top']))
	row5=cursor.fetchone()
	if row5 is None:
		r5['interval_name']=''
		r5['id']=0
	else:
		r5['interval_name']=row5['interval_name']
		r5['id']=row5['id']

	cursor.execute("SELECT interval_name,intervals.id from intervals WHERE interval_type='era' AND %f > age_top AND %f <= age_bottom AND %f < age_bottom AND %f >= age_top" % (row[x]['age_bottom'], row[x]['age_bottom'], row[x]['age_top'], row[x]['age_top']))
	row6=cursor.fetchone()
	if row6 is None:
		r6['interval_name']=''
		r6['id']=0
	else:
		r6['interval_name']=row6['interval_name']
		r6['id']=row6['id']

	cursor.execute("INSERT INTO lookup_unit_intervals (unit_id,FO_age,b_age,FO_interval,LO_age,t_age,LO_interval,epoch, epoch_id,period,period_id,age,age_id,era,era_id,eon,eon_id,FO_period,LO_period) VALUES ('%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%d','%s','%s')" % (row[x]['id'],row[x]['age_bottom'],row[x]['b_age'],row[x]['fname'],row[x]['age_top'],row[x]['t_age'],row[x]['lname'],r2['interval_name'], r2['id'],r3['interval_name'],r3['id'],r4['interval_name'],r4['id'],r6['interval_name'],r6['id'],r5['interval_name'],r5['id'],rFO['interval_name'],rLO['interval_name']))

#modifiy results for long-ranging units
cursor.execute("UPDATE lookup_unit_intervals set period=concat_WS('-',FO_period,LO_period) where period='' and FO_period not like ''")
cursor.execute("UPDATE lookup_unit_intervals set period=eon where period='' and eon='Archean'")
cursor.execute("UPDATE lookup_unit_intervals set period=concat_WS('-',FO_interval,LO_period) where FO_interval='Archean'")
cursor.execute("UPDATE lookup_unit_intervals set period='Precambrian' where period='' and t_age>=541")


## validate results
cursor.execute("SELECT count(*) N, (SELECT count(*) from lookup_unit_intervals) nn from units")
row = cursor.fetchone()
if row['N'] != row['nn'] :
	print "ERROR: inconsistent unit count in lookup_unit_intervals table"

print "Done with intervals table"

