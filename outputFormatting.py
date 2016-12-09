

#=====================================================================================

def convertCandIntsToNames(candsToConvert, candMap):
	convertedCands = []
	for i, candInt in enumerate(candsToConvert):
		if isinstance(candInt, int):
			candStr = candMap[candInt]
		else:
			candStr = convertCandIntsToNames(candInt, candMap)
		convertedCands.append(candStr)
	if isinstance(candsToConvert, tuple):
		convertedCands = tuple(convertedCands)
	# print("ToConvert: ", str(candsToConvert))
	# print("Converted: ", str(convertedCands))
	return convertedCands

#=====================================================================================

def getRankingString(ranking):
	rankStr = ""
	for i, cand in enumerate(ranking):
		if i != 0:
			rankStr += " > "
		rankStr += str(cand)
	return rankStr

#=====================================================================================

def getDictString(dict):
	dictStr = ""
	line = "{s}{key}: {val}{e}"
	for i, k in enumerate(dict.keys()):
		start = "\n{ " if (i == 0) else "  "
		end = "  }" if (i == len(dict)-1) else ",\n"
		dictStr += line.format(s=start, key=k, val=dict[k], e=end)
	return dictStr

#=====================================================================================




	