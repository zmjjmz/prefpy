

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

def convertDictionaryCandIntsToNames(candDictToConvert, candMap):
	convertedCands = dict()
	for candInt, val in candDictToConvert.items():
		candStr = candMap[candInt]
		if isinstance(val, dict):
			val = convertDictionaryCandIntsToNames(val, candMap)
		convertedCands[candStr] = val
	# print("ToConvert: ", getDictString(candDictToConvert))
	# print("Converted: ", getDictString(convertedCands))
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

def getDictString(dictionary):
	dictStr = ""
	line = "{s}{key}: {val}{e}"
	for i, k in enumerate(dictionary.keys()):
		start = "\n{ " if (i == 0) else "  "
		end = "  }" if (i == len(dictionary)-1) else ",\n"
		dictStr += line.format(s=start, key=k, val=dictionary[k], e=end)
	return dictStr

#=====================================================================================




