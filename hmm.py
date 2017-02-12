import numpy
import re

def learnparam(f):
	emit,transition,context,listwords = {},{},{},{}
	status = False
	previous = "<s>"
	context[previous] = context.get(previous, 0) + 1.0
	for wordtags in f:
		if wordtags == '. .\n':
			continue
		if wordtags == '\n':
			transition[previous+" "+"</s>"] = transition.get(previous+" "+"</s>", 0) + 1.0
			previous = "<s>"
			context[previous] = context.get(previous, 0) + 1.0
			listwords[word] = context.get(word, 0) + 1.0
			continue
		data = wordtags.rstrip().split(' ')
		word, tag = data[0].lower(), data[1]
		transition[previous+" "+tag] = transition.get(previous+" "+tag, 0) + 1.0
		context[tag] = context.get(tag, 0) + 1.0
		listwords[word] = context.get(word, 0) + 1.0
		emit[tag+" "+word] = emit.get(tag+" "+word,0) + 1.0
		previous = tag

	Pt, Pe = {}, {}
	for key, val in transition.iteritems():
		splitted = key.split(" ")
		Pt[splitted[0]] = Pt.get(splitted[0],{})
		Pt[splitted[0]][splitted[1]] = (val + 1) / (context[splitted[0]] + len(context))

	for key, val in emit.iteritems():
		splitted = key.split(" ")
		Pe[splitted[0]] = Pe.get(splitted[0],{})
		Pe[splitted[0]][splitted[1]] = val / context[splitted[0]]
	return {'Pt':Pt, 'Pe':Pe, 'context':context, 'listwords':listwords}

def hmmpostagger(words, probs):
	words = words.split(" ")
	pt, pe = probs['Pt'], probs['Pe']
	words[-1] = words[-1][:-1]
	possibletags, bestscore, bestedge = [key for key,i in probs['context'].iteritems()], [{"<s>":1}], [{"<s>":None}]
	for i in range(len(words)):
		bestscore.append({})
		bestedge.append({})
		for prev in bestscore[i]:
			for next in possibletags:
				pts = pt[prev].get(next, 1.0 / (probs['context'][prev] + len(probs['context'])))
				if words[i] in probs['listwords'] and next in pe:
					pes = pe[next].get(words[i], 0)
				else:
					if len(re.findall('[0-9]',words[i])) == 0:
						if next == 'NN': pes = 1.0
						else: pes = 0.0
					else:
						if next == 'CD': pes = 1.0
						else: pes = 0.0
				score = bestscore[i][prev] * pts * pes
				bestscore[i+1][next] = bestscore[i+1].get(next, score)
				if bestscore[i+1][next] <= score:
					bestscore[i+1][next], bestedge[i+1][next] = score, prev
	bestscore.append({})
	bestedge.append({})
	if words[0] == 'of' and words[1] == 'the' and words[2] == 'combined':
		print bestscore[-2]
	for prev  in bestscore[-2]:
		if prev in pt and "</s>" in pt[prev]:
			score = bestscore[-2][prev] * pt[prev]["</s>"]
			bestscore[-1]["</s>"] = bestscore[-1].get("</s>", score)
			if bestscore[-1]["</s>"] <= score:
				bestscore[-1]["</s>"], bestedge[-1]["</s>"] = score, prev

	path = []
	prev = "</s>"
	for i in range(len(bestscore)-1,1,-1):
		path.append(bestedge[i][prev])
		prev = bestedge[i][prev]
	path.reverse()
	return path

def testing(f, probs):
	sentence = ""
	tag = []
	total,tvalue = 0.0,0.0
	tp,fn,fp,tn = {},{},{},{}
	for i in probs['context']:
		tp[i],fn[i],fp[i],tn[i] = 0.0,0.0,0.0,0.0
	for wordtags in f:
		if wordtags == '. .\n':
			sentence = sentence[:-1]+"."
			postag = hmmpostagger(sentence, probs)
			for j in range(len(postag)):
				total += 1
				if tag[j] == postag[j]:
					tvalue += 1
				else:
					kata = sentence.split(" ")[j]
					if j == 0 and kata.lower() == 'of':
						print sentence.split(" ")[0],sentence.split(" ")[1],sentence.split(" ")[2],tag[j],postag[j]
				for i in probs['context']:
					if tag[j] == i:
						if tag[j] == postag[j]:
							tp[i] += 1
						else:
							fn[i] += 1
					else:
						if tag[j] == postag[j]:
							fp[i] += 1
						else:
							tn[i] += 1
			print "Current Accuration:",tvalue/total
			continue
		if wordtags == '\n':
			sentence = ""
			tag = []
			continue
		wtsplit = wordtags.rstrip().split(" ")
		sentence += wtsplit[0].lower()+" "
		tag.append(wtsplit[1])
	precision, recall = {},{}
	for i in probs['context']:
		precision[i] = tp[i] / (tp[i] + fp[i])
		recall[i] = tp[i] / (tp[i] + fn[i]) if (tp[i] + fn[i]) != 0 else "undefinied"
	return {'akurasi':tvalue/total, 'precision': precision, 'recall': recall}


def main():
	f = open('pos.train.txt','r')
	ftest = open('pos.test.txt','r')
	prob = learnparam(f)
	print len(prob['context'])
	result = testing(ftest,prob)
	for i in result['precision']:
		print i,"\n=============================="
		print "Precision:",result['precision'][i]
		print "recall:",result['recall'][i],"\n=============================="

	print result['akurasi']
main()