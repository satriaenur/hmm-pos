def learnparam(filetrain):
	emit,transition,context = [],[],[]
	status = False
	f = open(filetrain,'r')
	for line in f:
		if line==', ,\n':
			continue
		elif line=='\n':
			status = True
			continue
		if status:
			print line
			status = False

learnparam('pos.train.txt')
	
