#!/usr/bin/python

import sys
sys.path.insert(0, '/home/anthony/wiibalance/svn/trunk/python/build/lib.linux-i686-2.5/')
import cwiid
import sys
import time
import gdata.spreadsheet.service

def main():
	print 'Put Wiimote in discoverable mode now (press 1+2)...'
	global wiimote
	if len(sys.argv) > 1:
		wiimote = cwiid.Wiimote(sys.argv[1])
	else:
		wiimote = cwiid.Wiimote()

	wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
	wiimote.request_status()

	balance_calibration = wiimote.get_balance_cal()
	named_calibration = { 'right_top': balance_calibration[0],
						  'right_bottom': balance_calibration[1],
						  'left_top': balance_calibration[2],
						  'left_bottom': balance_calibration[3],
						}

	exit = False
	while not exit:
		print "Type q to quit, or anything else to report your weight"
		c = sys.stdin.read(1)
		if c == 'q':
			exit = True
			break
		wiimote.request_status()
		weight = (calcweight(wiimote.state['balance'], named_calibration))
		logweight(weight)

	return 0

def calcweight( readings, calibrations ):
	weight = 500
	for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
		reading = readings[sensor]
		calibration = calibrations[sensor]
		if reading > calibration[2]:
			print "Warning, %s reading above upper calibration value" % sensor
		print sensor
		print reading
		print calibration[0]
		print calibration[1]
		print calibration[2]
		oldWeight = weight
		if reading < calibration[1]:
			weight += 1700 * (reading - calibration[0]) / (calibration[1] - calibration[0])
		else:
			weight += 1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700
		print weight - oldWeight

	return str((weight / 100.0) * 2.2)
	
def logweight(weight):
	email = 'awestover89@gmail.com'
	password = 'ThisIsntMyRealPassword'
	spreadsheet_key = '0AtFA3oghJ3dOdGJ0NlFQdlc0WHlIa3EwcGptaGg2U1E'
	worksheet_id = 'od6'

	spr_client = gdata.spreadsheet.service.SpreadsheetsService()
	spr_client.email = email
	spr_client.password = password
	spr_client.source = 'Weight Logger'
	spr_client.ProgrammaticLogin()

	dict = {}
	dict['date'] = time.strftime('%m/%d/%Y')
	dict['time'] = time.strftime('%H:%M:%S')
	dict['weight'] = weight
	dict['source'] = 'AUTO'

	entry = spr_client.InsertRow(dict, spreadsheet_key, worksheet_id)
	if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
		print "Insert row succeeded."
	else:
		print "Insert row failed."

if __name__ == "__main__":
	sys.exit(main())
