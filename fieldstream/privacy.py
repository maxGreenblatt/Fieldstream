import time
import json
import privparser
import privacyDB
import privaction

# sudo apach2ctl graceful
# cd /home/haksoo/spotlight/spotlightdb && python manage.py runserver 128.97.93.26:8080

#UNDISCLOSED_MARK = '-'
UNDISCLOSED_MARK = 'UNDISCLOSED'

ROOT_PATH = '/home/max/spotlight/spotlightdb/fieldstream'
DEBUG_TAG = '##PRIVACY##:'
DUMP_DATA = False

def log(things):
	print DEBUG_TAG,
	print things

def convert_dot_to_tuples(dot_list):
	tup_list = []
	for str in dot_list:
		str_part = str.partition('.')
		tuple = (str_part[0], str_part[2])
		tup_list.append(tuple)
	return tup_list

def get_sensor_channel_tuples_from_virtual_sensor(virtual_sensor_list):
	dot_list = []
	for virtual_sensor in virtual_sensor_list:
		for vs_body in virtual_sensor.values():
			dot_list.append(vs_body['SensorChannelName'])
	return convert_dot_to_tuples(dot_list)

def get_time_tuples_from_time_conds(time_conds):
	print time_conds	
	return []

def get_loc_tuples_from_loc_conds(loc_conds):
	print loc_conds
	return []

def get_search_conds_from_query(query):
	search_conds = {}
	search_conds['SensorOwnerName'] = query['SensorOwnerName']
	if 'SensorName' in query:
		search_conds['SensorName'] = query['SensorName']
	else:
		search_conds['SensorName'] = []
	if 'SensorChannelName' in query:
		search_conds['SensorChannelName'] = convert_dot_to_tuples(query['SensorChannelName'])
	elif 'VirtualSensor' in query:
		search_conds['SensorChannelName'] = get_sensor_channel_tuples_from_virtual_sensor(query['VirtualSensor'])
	else:
		search_conds['SensorChannelName'] = []
	if 'Time' in query:
		search_conds['Time'] = privparser.parse_time(query['Time'])
	else:
		search_conds['Time'] = []
	if 'Time' in query:
		search_conds['Location'] = privparser.parse_location(query['Location'])
	else:
		search_conds['Location'] = []

	return search_conds

def get_rule_conds(rule):
	rule_conds = {}
	rule = rule['Condition']
	
	rule_conds['DataConsumer'] = rule['DataConsumer']

	if 'Sensor' in rule:
		if 'SensorName' in rule['Sensor']:
			rule_conds['SensorName'] = rule['Sensor']['SensorName']
		else:
			rule_conds['SensorName'] = []
		if 'SensorChannelName' in rule['Sensor']:
			rule_conds['SensorChannelName'] = convert_dot_to_tuples(rule['Sensor']['SensorChannelName'])
		else:
			rule_conds['SensorChannelName'] = []
	else:
		rule_conds['SensorName'] = []
		rule_conds['SensorChannelName'] = []

	if 'Time' in rule:
		rule_conds['Time'] = privparser.parse_time(rule['Time'])
	else:
		rule_conds['Time'] = []
	if 'Location' in rule:
		rule_conds['Location'] = privparser.parse_location(rule['Location'])
	else:	
		rule_conds['Location'] = []

	return rule_conds

def find_applicable_rules(requestor, search_conds, rules):
	#print '------- find_applicable_rules --------'

	app_rules = []
	
	for i, cur_rule in enumerate(rules):

		#print '==iter %d==' % i

		owner = cur_rule.owner.username
		rule = json.loads(cur_rule.rule)
	
		# check if search_conds['SensorOwnerName'] matchs rules[OwnerID].
		if not search_conds['SensorOwnerName'] == owner:
			continue

		# get conditions for current rule
		rule_conds = get_rule_conds(rule)

		# check if requestor is in rule_conds[DataConsumer]
		# TODO: check GROUP and STUDY -> ask Max.
		if not requestor.username in rule_conds['DataConsumer']:
			continue

		# check if earch_conds[Sensor] and rule_conds[Sensor] has something common
		#print 'search_conds[SensorName]:', search_conds['SensorName']
		#print 'search_conds[SensorChannelName]:', search_conds['SensorChannelName']
		#print 'rule_conds[SensorName]:', rule_conds['SensorName']
		#print 'rule_conds[SensorChannelName]:', rule_conds['SensorChannelName']
		
		haveCommon = False
		for ssn in search_conds['SensorName']:
			for rsn in rule_conds['SensorName']:
				if ssn == rsn:
					haveCommon = True
			for rscn in rule_conds['SensorChannelName']:
				if ssn == rscn[0]:
					haveCommon = True
		for sscn in search_conds['SensorChannelName']:
			for rsn in rule_conds['SensorName']:
				if sscn[0] == rsn:
					haveCommon = True
			for rscn in rule_conds['SensorChannelName']:
				if sscn == rscn:
					haveCommon = True

		#print 'haveCommon:', haveCommon

		if not haveCommon:
			continue

		# check if AND(search_conds['Time'], rule_conds[Time]) has something
		#print 'search_conds[Time]:', search_conds['Time']
		#print 'rule_conds[Time]:', rule_conds['Time']
		if search_conds['Time']	and rule_conds['Time']:
			#print 'AND:', privparser.AND(search_conds['Time'], rule_conds['Time'])
			if not privparser.AND(search_conds['Time'], rule_conds['Time']):
				continue

		# check if search_conds['Location'] and rule_conds[Location] has common area
		#print 'search_conds[Location]:', search_conds['Location']
		#print 'rule_conds[Location]:', rule_conds['Location']
		if search_conds['Location'] and rule_conds['Location']:
			if not privparser.have_common_area(search_conds['Location'], rule_conds['Location']):
				continue
	
		# current rule is applicable.
		app_rules.append(cur_rule)

	# return applicable rules
	return app_rules

def reduce_search_conds(search_conds, rules):
	print '----- reduce_search_conds() -----'

	# get allow rules.
	allow_rules = []
	for cur_rule in rules:
		rule = json.loads(cur_rule.rule)
		if rule['Action'] == 'Allow':
			allow_rules.append(rule)
	
	if not allow_rules:
		# there no Allow rules... make search_conds empty
		print 'We have no allow rules...'
		return None

	# get deny rules.
	deny_rules = []
	for cur_rule in rules:
		rule = json.loads(cur_rule.rule)
		if rule['Action'] == 'Deny':
			deny_rules.append(rule)

	if not deny_rules:
		# nothing to do with search condition.
		print 'We have no deny rules...'
		return search_conds

	# TODO: looking at rules with "Deny" action w/o "Value" condition.

	# merge the deny rules
	rule_conds_list = []
	for rule in deny_rules:
		rule_conds = get_rule_conds(rule)
		rule_conds_list.append(rule_conds)
	rule_conds = merge_rule_conds(rule_conds_list)

	print 'deny_rule_conds:', rule_conds
	print 'search_conds:', search_conds
	
	something_in_sensor = False

	#SensorName
	new_sn = []
	if search_conds['SensorName']:
		something_in_sensor = True
	for sn_sc in search_conds['SensorName']:
		is_found = False
		for sn_rc in rule_conds['SensorName']:
			if sn_sc == sn_rc:
				is_found = True
				break
		if not is_found:
			new_sn.append(sn_sc)
	
	search_conds['SensorName'] = new_sn

	#SensorChannelName
	new_scn = []
	if search_conds['SensorChannelName']:
		something_in_sensor = True
	for scn_sc in search_conds['SensorChannelName']:
		is_found = False

		for sn_rc in rule_conds['SensorName']:
			if scn_sc[0] == sn_rc:
				is_found = True
				break
	
		for scn_rc in rule_conds['SensorChannelName']:
			if scn_sc == scn_rc:
				is_found = True
				break
		
		if not is_found:
			new_scn.append(scn_sc)

	search_conds['SensorChannelName'] = new_scn

	# check if there were some condition for sensor but nothing is left.
	if something_in_sensor and not new_sn and not new_scn:
		return None

	#Time
	#A - B = A AND NOT(B)
	if search_conds['Time'] and rule_conds['Time']:
		search_conds['Time'] = privparser.AND(search_conds['Time'], privparser.NOT(rule_conds['Time']))
	elif not search_conds['Time'] and rule_conds['Time']:
		search_conds['Time'] = privparser.NOT(rule_conds['Time'])

	#Location
	for loc in rule_conds['Location']:
		search_conds['Location'].append((loc[0], loc[1], loc[2], loc[3], loc[4], loc[5], loc[6], loc[7], not loc[8]))

	print 'reduced search conds:', search_conds

	return search_conds

def do_query(search_conds, waveseg_list, is_post_process):
	# is_post_process = False: reserve Time, Location X, Y, and Z for rule processing
	# is_post_process = True: chop out Time, Location X, Y, and Z as needed in search_conds.

	if is_post_process:
		print '----- do_query() post process -----'
	else:
		print '----- do_query() -----'

	print 'search_conds:', search_conds

	result_wsl = []

	for waveseg in waveseg_list:

		# find waveseg satisfying search_conds

		# SensorOwnerName: gauranteed by DB

		nwseg = {}
		nwseg['SensorNode'] = waveseg['SensorNode']
		nwseg['StartTime'] = waveseg['StartTime']
		nwseg['SamplingInterval'] = waveseg['SamplingInterval']
		nwseg['EndTime'] = waveseg['EndTime']
		nwseg['StaticLocation'] = waveseg['StaticLocation']
		nwseg['ValueBlobFormat'] = []
		nwseg['ValueBlob'] = []

		#print 'nwseg:', nwseg
		#print 'waveseg:', waveseg

		# SensorName
		if is_post_process: 
			idx_list = []
		else:
			idx_list = [0, 1, 2, 3]
		if ((not search_conds['SensorName'] and not search_conds['SensorChannelName']) or
				(waveseg['SensorNode'] in search_conds['SensorName'])):
			idx_list = range(0, len(waveseg['ValueBlobFormat']))

		# SensorChannelName 
		for scn in search_conds['SensorChannelName']:
			if scn[0] == waveseg['SensorNode']:
				if not (scn[0] in search_conds['SensorName']): 
					if scn[1] in waveseg['ValueBlobFormat']:
						idx = waveseg['ValueBlobFormat'].index(scn[1])
						if not idx in idx_list:
							idx_list.append(idx)
	
		#print idx_list

		for idx in idx_list:
			nwseg['ValueBlobFormat'].append(waveseg['ValueBlobFormat'][idx])

		# Time and Location
		for values in waveseg['ValueBlob']:
			if is_post_process:
				is_time = True
				is_loc = True
			else:
				is_time = is_time_in(values[0], search_conds['Time'])
				is_loc  = is_loc_in((values[1], values[2], values[3]), search_conds['Location'])
			if is_time and is_loc:
				# copy the values
				nvals = []
				for idx in idx_list:
					nvals.append(values[idx])
				if nvals:
					nwseg['ValueBlob'].append(nvals)

		# Finally, add this waveseg to result.
		if nwseg['ValueBlob']:
			result_wsl.append(nwseg)

	return result_wsl

# TODO: semantic of merging ambiguous.
def merge_rule_conds(rclist):
	#print '-------- rclist --------'
	#for rc in rclist:
	#	print rc

	mrc = {}

	mrc['DataConsumer'] = []
	mrc['SensorName'] = []
	mrc['SensorChannelName'] = []
	mrc['Time'] = []
	mrc['Location'] = []

	for rc in rclist:
		for dc in rc['DataConsumer']:
			if not (dc in mrc['DataConsumer']):
				mrc['DataConsumer'].append(dc)
		for sn in rc['SensorName']:
			if not (sn in mrc['SensorName']):
				mrc['SensorName'].append(sn)
		for scn in rc['SensorChannelName']:
			if not (scn in mrc['SensorChannelName']):
				mrc['SensorChannelName'].append(scn)
		if rc['Time']:
			if not mrc['Time']:
				mrc['Time'] = rc['Time']
			else:
				mrc['Time'] = privparser.OR(mrc['Time'], rc['Time'])
		for loc in rc['Location']:
			mrc['Location'].append(loc)

	#print '------- mrc --------'
	#print mrc

	return mrc

def is_time_in(t, t_cond):
	#print t
	#print t_cond
	
	if not t_cond or not t:
		return True

	for tr in t_cond:
		c1 = False
		c2 = False
		if not tr[0]:
			c1 = True
		else:
			if tr[1]: # GTEQ
				if tr[0] <= t:
					c1 = True
			else: # GT
				if tr[0] < t:
					c1 = True

		if not tr[2]:
			c2 = True
		else:
			if tr[3]: # LTEQ
				if t <= tr[2]:
					c2 = True
			else: # LT
				if t < tr[2]:
					c2 = True

		if c1 and c2:
			#print 'True at:', tr
			return True

	return False

def is_loc_in(loc, loc_cond):
	#print loc
	#print loc_cond
	
	if loc == (None, None, None) or not loc_cond:
		return True

	is_in = False
	is_notin = False
	for lr in loc_cond:
		is_in_rect = lr[0] <= loc[0] and loc[0] <= lr[4] and lr[6] <= loc[1] and loc[1] <= lr[2]
		if not lr[8]: # if it's IN location.
			is_in = True
			if is_in_rect:
				return True
		else: # if it's NOT IN location
			is_notin = True
			if is_in_rect:
				return False
	
	if not is_in and is_notin:
		return True
	
	return False

def	do_allow_deny_action(requestor, rules, waveseg_list, is_allow):
	if is_allow:
		print '----- do_allow_action() -----'
	else:
		print '----- do_deny_action() -----'

	result_wsl = []

	# get allow or deny rules.
	my_rules = []
	for cur_rule in rules:
		rule = json.loads(cur_rule.rule)
		if ((is_allow     and rule['Action'] == 'Allow') or
				(not is_allow and rule['Action'] == 'Deny' )):
			my_rules.append(rule)

	if not is_allow and not my_rules:
		print 'We have no deny rules...'
		return waveseg_list

	if is_allow and not my_rules:
		# there no Allow rules... deny everything
		print 'We have no allow rules. deny everything.'
		is_allow = False

	# merge the allow rules
	rule_conds_list = []
	for rule in my_rules:
		rule_conds = get_rule_conds(rule)
		rule_conds_list.append(rule_conds)

	rule_conds = merge_rule_conds(rule_conds_list)

	print 'rule_conds:', rule_conds

	for waveseg in waveseg_list:

		# Find waveseg satisfying following conditions.
		# DataConsumer: already checked in find_applicable_rules()

		# Find sensor channels from SensorName and SensorChannelName
		idx_list = []
		
		# from SensorName ...
		if ((not rule_conds['SensorName'] and not rule_conds['SensorChannelName']) or
				(waveseg['SensorNode'] in rule_conds['SensorName'])):
			idx_list = range(0, len(waveseg['ValueBlobFormat']))

		# from SensorChannelName ...
		for scn in rule_conds['SensorChannelName']:
			if scn[0] == waveseg['SensorNode']:
				if not (scn[0] in rule_conds['SensorName']): 
					if scn[1] in waveseg['ValueBlobFormat']:
						idx_list.append(waveseg['ValueBlobFormat'].index(scn[1]))
	
		# Loop trough all values and mark undisclosed values
		for values in waveseg['ValueBlob']:
			
			# Check Time and Location
			is_time = is_time_in(values[0], rule_conds['Time'])
			is_loc  = is_loc_in((values[1], values[2], values[3]), rule_conds['Location'])
		
			if not (is_time and is_loc):
				if is_allow:
					# mark all sensor channels undisclosed
					for i, v in enumerate(values):
						values[i] = UNDISCLOSED_MARK
				continue
		
			# Check Value: TODO

			# Check SensorChannel
			for i, v in enumerate(values):
				if ( (is_allow     and not (i in idx_list)) or
				     (not is_allow and (i in idx_list))):
					values[i] = UNDISCLOSED_MARK

		# Finally, add this waveseg to result.
		result_wsl.append(waveseg)

	return result_wsl


def do_action(requestor, rules, waveseg_list):
	
	# Process Allow action.
	waveseg_list = do_allow_deny_action(requestor, rules, waveseg_list, True)
	
	if DUMP_DATA:
		print '----- waveseg_list after do_allow_action() -----'
		for waveseg in waveseg_list:
			print waveseg

	# Process Deny Action
	waveseg_list = do_allow_deny_action(requestor, rules, waveseg_list, False)
	
	if DUMP_DATA:
		print '----- waveseg_list after do_deny_action() -----'
		for waveseg in waveseg_list:
			print waveseg
	
	# Process privacy primitive actions
	waveseg_list = privaction.do_privacy_actions(requestor, rules, waveseg_list)

	if DUMP_DATA:
		print '----- waveseg_list after do_privacy_actions() -----'
		for waveseg in waveseg_list:
			print waveseg

	return waveseg_list


def do_virtual_sensor(virt_sensor, waveseg_list):
	return waveseg_list

def convert_waveseg(waveseg_list):
	list = []
	
	for waveseg in waveseg_list:
		mdict = {}
		mdict['SensorNode'] = waveseg.sensorNode.name
		mdict['StartTime'] = time.mktime(waveseg.startTime.timetuple())
		mdict['EndTime'] = time.mktime(waveseg.endTime.timetuple())
		mdict['SamplingInterval'] = waveseg.sampleInterval

		if waveseg.staticLocationX == None and waveseg.staticLocationY == None and waveseg.staticLocationH == None:
			mdict['StaticLocation'] = None
		else:
			mdict['StaticLocation'] = {}
			mdict['StaticLocation']['X'] = waveseg.staticLocationX
			mdict['StaticLocation']['Y'] = waveseg.staticLocationY
			mdict['StaticLocation']['Z'] = waveseg.staticLocationH
		mdict['ValueBlobFormat'] = json.loads(waveseg.valuesFormat);
		mdict['ValueBlob'] = json.loads(waveseg.values)

		list.append(mdict)

	return list

def optimize_waveseg_list(waveseg_list):
	print '----- optimize_waveseg_list -----'

	return waveseg_list

def process_privacy(requestor, query):
	log('Start of process_privacy()')

	# get query
	query = query['Query']
	#log(json.dumps(query, indent=4))

	# Generate search condition dictionary from query
	search_conds = get_search_conds_from_query(query)

	print '----- search conditions -----'
	print search_conds

	# DBInterface:  Get a Rule list from the database.
	#
	#	Returns:
	# list of privacyRule object
	#
	# Argumetns:
	# search_conds['SensorOwnerName']: just a string. e.g. 'max'
	# search_conds['SensorName']: list of SensorName. e.g. ['Raritan 1', 'ShimmerDE89', ... ]
	# search_conds['SensorChannelName']: list of tuple (SensorName, SensorChannelName). e.g. [ ('Raritan 1', 'RealPower 1'), ... ]
	# when []: no condition.
	rules = privacyDB.get_privacy_rules(requestor, search_conds['SensorOwnerName'], search_conds['SensorName'], search_conds['SensorChannelName'])

	print '----- privacy rules from DB -----'
	for rule in rules:
		print rule.rule

	# Find Rules that apply to current query 
	# by comparing current search_conds and "Condition" key in each rules.
	rules = find_applicable_rules(requestor, search_conds, rules)

	print '----- after finding applicable rules -----'
	for rule in rules:
		print rule.rule

	# Reduce waveseg search criteria based on the rules
	search_conds = reduce_search_conds(search_conds, rules)
		
	# If there is no search condition left, return empty waveseg list
	if search_conds == None:
		print 'no search condition left.'
		return '[]' # json empty list



	# DBInterface ###
	# Get a WaveSeg list from the database with reduced search condition.
	waveseg_list = privacyDB.get_wavesegs(search_conds['SensorOwnerName'], search_conds['SensorName'], search_conds['SensorChannelName'], search_conds['Time'], search_conds['Location'])
	#
	# Arguments: (True: inclusive, False: exclusive)
	# search_conds['Time']: [ (start, T/F, end, T/F), ... ]
	#   special cases: (start, T/F, None, T/F), (None, T/F, end, T/F)
	#
	# search_conds['Location']: [ (upperleft X, T/F, upperleft Y, T/F, bottomright X, T/F, bottomright Y, T/F, T/F), ... ]
	#                 T/F at the end: whether it is NOT operator (True: NOT)
	# when []: no condition.

	# convert the waveseg to dictionary
	waveseg_list = convert_waveseg(waveseg_list)

	print '----- after privacyDB.get_wavesegs() -----'
	print '# of wavesegs:', len(waveseg_list)

	if DUMP_DATA:
		print '----- waveseg_list from DB -----'
		for waveseg in waveseg_list:
			print waveseg

	# Reduce waveseg with search_conds.
	# This will chop out sensor channels and value blob not requested.
	# Time and location will remain for privacy rule processing
	# They will be chopped out after do_action()
	waveseg_list = do_query(search_conds, waveseg_list, False)

	if DUMP_DATA:
		print '----- waveseg_list after do_query() -----'
		for waveseg in waveseg_list:
			print waveseg
	
	# Perform "Action" part of each rules on the waveseg list.
	# This will reduce or modify data within wave seg.
	waveseg_list = do_action(requestor, rules, waveseg_list)

	# Optimize waveseg
	waveseg_list = optimize_waveseg_list(waveseg_list)

	# Perform virtual sensor process.
	if 'VirtualSensor' in query:
		waveseg_list = do_virtual_sensor(query['VirtualSensor'], waveseg_list)

	# Do post process for query. 
	# Chop out Time, Location X,Y,Z as needed in search conds.
	waveseg_list = do_query(search_conds, waveseg_list, True)

	if DUMP_DATA:
		print '----- waveseg_list after do_query() post process -----'
		for waveseg in waveseg_list:
			print waveseg
	
	# Finally, return the final list of WaveSeg
	log('Return from process_privacy()')
	
	return json.dumps(waveseg_list)

# test script
def main():
	global ROOT_PATH
	ROOT_PATH = '.'
	filename = 'example_query2.json'
	fp = open(filename, 'r')
	query = json.load(fp)

	ret_string = process_privacy(None, query)

	print 'Return =', ret_string

if __name__ == "__main__":
	main()

