import math

START, SEQ, END, EEQ = range(4)

def flatten(t):
	flat_t = []
	for tp in t:
		for tp_element in tp:
			flat_t.append(tp_element)
	return flat_t

def GT(t):
	return [(t, False, None, None)]

def LT(t):
	return [(None, None, t, False)]

def GTEQ(t):
	return [(t, True, None, None)]

def LTEQ(t):
	return [(None, None, t, True)]

def EQ(t):
	return [(t, True, t, True)]

def NOT(t):
	ft = flatten(t)
	new_t = []

	# handle first item
	if ft[0] is not None:
		assert ft[1] is not None
		new_t.append((None, None, ft[0], not ft[1]))
	
	i = -2
	for i in range(2, len(ft)-3, 4):
		assert ft[i] is not None
		new_t.append((ft[i], not ft[i+1], ft[i+2], not ft[i+3]))
	
	# handle last item
	if ft[i+4] is not None:
		assert ft[i+5] is not None
		new_t.append((ft[i+4], not ft[i+5], None, None))

	return new_t

def left_overlap(t1, t2):
	cond1 = False
	if t1[START] == None and t2[START] != None:
		cond1 = True
	elif t1[START] < t2[START]:
		cond1 = True
	elif t1[START] == t2[START] and (t1[SEQ] and not t2[SEQ]):
			cond1 = True

	cond2 = False
	if t2[END] == None and t1[END] != None:
		cond2 = True
	elif t1[END] < t2[END]:
		cond2 = True
	elif t1[END] == t2[END] and (not t1[EEQ] and t2[EEQ]):
			cond2 = True

	cond3 = False
	if t1[END] == None or t2[START] == None:
		return False
	if t1[END] > t2[START]:
		cond3 = True
	elif t1[END] == t2[START] and (t1[EEQ] or t2[SEQ]):
		cond3 = True

	return cond1 and cond2 and cond3

def right_overlap(t1, t2):
	return left_overlap(t2, t1)

def contained(t1, t2):
	cond1 = False
	if t2[START] == None and t1[START] == None:
		cond1 = True
	elif t2[START] < t1[START]:
		cond1 = True
	elif t2[START] == t1[START] and not ( not t2[SEQ] and t1[SEQ] ):
		cond1 = True
		
	cond2 = False
	if t1[END] == None and t2[END] == None:
		cond2 = True
	elif t1[END] < t2[END]:
		cond2 = True
	elif t1[END] == t2[END] and not ( t1[EEQ] and not t2[EEQ] ):
		cond2 = True

	return cond1 and cond2

def contains(t1, t2):
	return contained(t2, t1)

def leftof(t1, t2):
	if t1[END] == None or t2[START] == None:
		return False
	if t1[END] < t2[START]:
		return True
	elif t1[END] == t2[START] and ( not t1[EEQ] and not t2[SEQ] ):
		return True
	return False

def rightof(t1, t2):
	return leftof(t2, t1)

def OR(t1, t2):
	i = 0; j = 0; new_tlist = []
	new_t = None
	ta = t1[i]
	tb = t2[j]
	while True:
		if left_overlap(ta, tb):
			#print 'left_overlap'
			new_t = (ta[START], ta[SEQ], tb[END], tb[EEQ])
			#print 'new_t =', new_t
			i += 1
			if i >= len(t1):
				j += 1
				break
			ta = t1[i]
			tb = new_t
		elif right_overlap(ta, tb):
			#print 'right_overlap'
			new_t = (tb[START], tb[SEQ], ta[END], ta[EEQ])
			#print 'new_t =', new_t
			j += 1
			if j >= len(t2):
				i += 1
				break
			ta = new_t
			tb = t2[j]
		elif contained(ta, tb):
			#print 'contained'
			new_t = tb
			#print 'new_t =', new_t
			i += 1
			if i >= len(t1):
				j += 1
				break
			ta = t1[i]
			tb = new_t
		elif contains(ta, tb):
			#print 'contains'
			new_t = ta
			#print 'new_t =', new_t
			j += 1
			if j >= len(t2): 
				i += 1
				break
			ta = new_t
			tb = t2[j]
		elif leftof(ta, tb):
			#print 'leftof'
			new_tlist.append(ta)
			new_t = None
			#print 'new_tlist =', new_tlist
			i += 1
			if i >= len(t1): 
				break
			ta = t1[i]
			tb = t2[j]
		elif rightof(ta, tb):
			#print 'rightof'
			new_tlist.append(tb)
			new_t = None
			#print 'new_tlist =', new_tlist
			j += 1
			if j >= len(t2): 
				break
			ta = t1[i]
			tb = t2[j]

	#print 'append last new_t'
	if new_t is not None:
		new_tlist.append(new_t)
	#print new_tlist

	#print 'append remaining t'
	if i < len(t1):
		for k in range(i, len(t1)):
			new_tlist.append(t1[k])
	if j < len(t2):
		for k in range(j, len(t2)):
			new_tlist.append(t2[k])
	#print new_tlist

	return new_tlist

def AND(t1, t2):
	i = 0; j = 0; new_tlist = []
	while i < len(t1) and j < len(t2):
		if left_overlap(t1[i], t2[j]):
			#print 'left_overlap'
			if not (t1[i][END] == t2[j][START] and not (t1[i][SEQ] and t2[i][EEQ])):
				new_tlist.append((t2[j][START], t2[j][SEQ], t1[i][END], t1[i][EEQ]))
			i += 1
		elif right_overlap(t1[i], t2[j]):
			#print 'right_overlap'
			if not (t1[i][START] == t2[j][END] and not (t1[i][SEQ] and t2[i][EEQ])):
				new_tlist.append((t1[i][START], t1[i][SEQ], t2[j][END], t2[j][EEQ]))
			j += 1
		elif contained(t1[i], t2[j]):
			#print 'contained'
			new_tlist.append(t1[i])
			i += 1
		elif contains(t1[i], t2[j]):
			#print 'contains'
			new_tlist.append(t2[j])
			j += 1
		elif leftof(t1[i], t2[j]):
			#print 'leftof'
			i += 1
		elif rightof(t1[i], t2[j]):
			#print 'rightof'
			j += 1

	return new_tlist

def get_time_tuples_from_time_range(time_range):
	return time_range

def rec_parse_time(time_dic):
	item = time_dic.items()
	assert len(item) == 1
	item = item[0]

	#print item
	tlist = []

	#print item[0]
	if item[0] == 'LT':
		return LT(item[1])
	elif item[0] == 'GT':
		return GT(item[1])
	elif item[0] == 'LTEQ':
		return LTEQ(item[1])
	elif item[0] == 'GTEQ':
		return GTEQ(item[1])
	elif item[0] == 'EQ':
		return EQ(item[1])
	elif item[0] == 'AND':
		tlist = AND(rec_parse_time(item[1][0]), rec_parse_time(item[1][1]))
		for i in range(2, len(item[1])):
			tlist = AND(tlist, rec_parse_time(item[1][i]))
	elif item[0] == 'OR':
		tlist = OR(rec_parse_time(item[1][0]), rec_parse_time(item[1][1]))
		for i in range(2, len(item[1])):
			tlist = OR(tlist, rec_parse_time(item[1][i]))
	elif item[0] == 'NOT':
		tlist = NOT(rec_parse_time(item[1]))
	else:
		assert False

	#print tlist
	return tlist

def parse_time(time_query):
	if type(time_query).__name__ == 'dict':
		time_range = time_query['TimeRange']
		if type(time_range).__name__ == 'list':
			return get_time_tuples_from_time_range(time_range)
		elif type(time_range).__name__ == 'dict':
			return rec_parse_time(time_range)
	elif time_query == 'Any':
		#return [(None, None, None, None)]
		return []
		
	# Unkown time query.
	assert False

# gps coords --> km (http://en.wikipedia.org/wiki/Geographic_coordinate_system)
MR = 6367.449
#latitude 1 degree = 110.9 km
#1 km = 1 / 110.9 degree
LAT_1KM_DEG = 1.0 / 110.9
#longitude 1 degree = PI / 180 * cos(lat) * (6367.449 km)
#1 km = 1 / ( PI / 180 * cos(lat) * 6367.449 km )
LON_1KM_DEG = 1.0 / ( math.pi / 180.0 * math.cos(60.0 * math.pi / 180.0) * MR )

def get_gpscoords_from_in(in_dict):

	coords = in_dict['CenterCoordinates']

	lon_deg = in_dict['Distance'][0] / 2.0 * LON_1KM_DEG
	lat_deg = in_dict['Distance'][1] / 2.0 * LAT_1KM_DEG

	ret = [ (coords[1]-lon_deg, False, coords[0]+lat_deg, False, coords[1]+lon_deg, False, coords[0]-lat_deg, False, False) ]

	return ret

def have_common_area(reg1, reg2):
	for r1 in reg1:
		for r2 in reg2:
			if r1[0] < r2[4] and r1[2] > r2[6] and r1[4] > r2[0] and r1[6] < r2[2]:
				return True
	return False

def parse_location(location_query):
	if type(location_query).__name__ == 'dict':
		ret = []
		if 'In' in location_query:
			ret = get_gpscoords_from_in(location_query['In'])
		return ret
	elif location_query == 'Any':
		return []
	
	# Unkown location query
	assert False


def main():
	 t1 = [(None,None,0,True),         (15,True,20,True),        (30,True,40,True),                ]
	 t2 = [                     (5,True,15,True),        (25,True,35,True),     (40,False,55,False),   (80,True,90,True)]

	 #t1 = [(10, False, 20, True)]
	 #t2 = [(30, True, 40, False)]
	 #print NOT(t1)
	 #print AND(t1, t2)
	 print OR(t1, t2)

if __name__ == '__main__':
	main()
