import urllib2, urllib, csv, re, multiprocessing, time

def getCards():
	rawCards = open("cards.csv", 'r+')
	cards = []
	reader = csv.reader(rawCards, delimiter = ",")
	for card in reader:
		card[3]=int(card[3])
		if len(card)>4:
			for i in range(4,len(card)):
				card[i]=float(card[i])
		cards.append(card)
	rawCards.close()
	return cards

def setCode(cset):
	if cset.lower()=="ths":
		return "Theros"
	elif cset.lower()=="bng":
		return "Born of the Gods"
	elif cset.lower()=="rtr":
		return "Return to Ravnica"
	elif cset.lower()=="jou":
		return "Journey into Nyx"
	elif cset.lower()=="gtc":
		return "Gatecrash"
	elif cset.lower()=="dgm":
		return "Dragon's Maze"
	else:
		return ""

def binarySearch(cards, key, imin, imax):
 	if imax < imin:
 		return -1
 	else:
 		imid = (imin + imax) / 2
 		if cards[imid][0:2]>key:
 			return binarySearch(cards, key, imin, imid-1)
 		elif cards[imid][0:2]<key:
 			return binarySearch(cards, key, imid+1, imax)
 		else:
 			return imid

#returns index of card via binary search
def getCard(cardName, cardSet):
	key = []
	key.append(cardName)
	key.append(cardSet)
	cards = sorted(getCards())
	return binarySearch(cards, key,0, len(cards)-1)

def getQty(cardName, cardSet):
	index = getCard(cardName, cardSet)
	if index<0:
		return 0
	else:
		return getCards()[index][3]

# updates single card's data. returns list of cards
def updateCardRaw(name, cset):
	index = getCard(name, cset)
	if index <0:
		return
	cardList = getCards()
	row = cardList[index]
	url = "http://magic.tcgplayer.com/db/magic_single_card.asp?cn="+urllib.quote(name, ",")+"&sn="+urllib.quote(cset)
	page = urllib2.urlopen(url).read()
	prices = []
	prices = re.findall('\<B\>\$(\d*\.?\d+)', page)
	rarity = re.findall("Rarity.*\n.*\n.*\n\s*(\w*)", page)
	row[2]=rarity[0]
	if len(row)>=5:
		row = row[0:4]
	for thing in prices:
		row.append(float(thing))
	return cardList

# takes list of cards and writes to .csv
def writeCards(cards):
	cards = sorted(cards)
	rawCards = open("cards.csv", "r+")
	writer = csv.writer(rawCards, delimiter = ",", quoting = csv.QUOTE_NONNUMERIC)
	writer.writerows(cards)
	rawCards.close()

# updates single card and writes to .csv
def updateCard(data):
	writeCards(updateCardRaw(data[0], data[1]))

#adds card to sheet
def addCard(name, cset):
	#First check to see if one already exists
	index = getCard(name, cset)
	if index != -1:
		cardList = getCards()
		cardList[index][3]+=1
		writeCards(sorted(cardList))
	#otherwise increment quantity
	else:
		cardList = getCards()
		cardList.append([name, cset, "dummy",1])
		writeCards(sorted(cardList))
	updateCard([name,cset])

def addCardq(name, cset, qty):
	index = getCard(name, cset)
	if index != -1:
		cardList = getCards()
		cardList[index][3]+=qty
		writeCards(cardList)
	else:
		cardList = getCards()
		cardList.append([name, cset, "dummy", qty])
		writeCards(sorted(cardList))
	updateCard([name,cset])

def updateRares():
	cards = getCards()
	rares = []
	for card in cards:
		if card[2]=="Rare" or card[2]=="Mythic":
			rares.append(card)
	pool = multiprocessing.Pool(processes=4)
	pool.map(updateCard, rares)

def getWorth():
	cards = getCards()
	worth = [0.00,0.00,0.00]
	for card in cards:
		worth[0] += card[3]*card[4]
		worth[1] += card[3]*card[5]
		worth[2] += card[3]*card[6]
	return worth

def prompt():
	mode = raw_input("Select mode: ")

	while mode != "exit":
		if mode=="add" or mode=="a":
			card = "j"
			while card != "done":
				card = raw_input("Enter Card (Name;Set): ")
				if ";" in card:
					dat = card.split(";")
					if "how many" in card.lower():
						print getQty(dat[1],setCode(dat[2]))
					elif len(dat)==2:
						addCard(dat[0],setCode(dat[1]))
					elif len(dat)==3:
						addCardq(dat[0],setCode(dat[1]),int(dat[2]))

		if mode =="update rares":
			updateRares()
		if mode =="qty":
			card = "j"
			while card != "done":
				card = raw_input("Enter Card(Name;Set): ")
				if ";" in card:
					dat = card.split(";")
					print getQty(dat[0],setCode(dat[1]))
		if mode == "worth":
			print getWorth()

		mode = raw_input("Select mode: ")
###########################################################################################
prompt()