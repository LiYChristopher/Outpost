''' Very basic utility functions that help you backup MongoDB database,
saving blog data to a dump folder containing BSON documents of all entries.'''

import subprocess
from config import MONGODB_HOST, MONGODB_PORT


def dump_backup(database, host=MONGODB_HOST,
				port=MONGODB_PORT, output='dump'):
	''' Runs the mongodump terminal utility function to write
	database data as a BSON file to a database.'''
	try:
		cmd = 'mongodump --host {} --port {} -o {} --db {}'.format(host, port, output, database)
		dump = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
	except Exception, e:
		raise Exception('Check your inputs - database name,'
						'for valid host/port, valid output location.')
	return


def dump_restore(database, db_loc, host=MONGODB_HOST,
				 port=MONGODB_PORT, output='dump'):
	''' Runs the mongorestore terminal utility function to restore
	a database from local directory `db_loc`. '''
	try:
		cmd = 'mongorestore --host {} --port {} --db {} {} --drop'.format(host, port, database, db_loc)
		restore = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
		print restore
	except Exception, e:
		print e
		raise Exception('Check your inputs - database name,'
						'for valid host/port, valid output location.')
	return