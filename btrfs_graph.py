#!/usr/bin/python

from Tkinter import *
from graphviz import Graph
from pyparsing import *
import sys
import os
import subprocess

reload(sys)
sys.setdefaultencoding('utf-8')

inode = []

def mainParsing():
	lines = ""
	args = ["sudo", "btrfs-debug-tree"]
	d = enterDevice.get()
	args.append(str(d))
	#path = args[3].split('/')
	#path.insert(0, "..")

	p = subprocess.Popen(args, stdout=subprocess.PIPE)
	lines, error = p.communicate()
	lines = lines.splitlines(True)

	key = Suppress('key (') +  Word(alphanums + '_' + '-')('id') + Word(alphanums + '_' + '-')('type') + \
		Word(alphanums + '_' + '-')('offset') + Suppress(')')
	name = Suppress('name:') + Word(alphanums  + '_' + '.'  + '{' + '}' + '-')('name')


	leaf = Suppress('leaf') + Word(nums)('leaf')
	num_items = Suppress('items') + Word(nums)('items')
	free_space = Suppress('free space') + Word(nums)('free_space')
	generation = Suppress('generation') + Word(nums)('generation')
	owner = Suppress('owner') + Word(nums)('owner')
	parseLeaf = leaf + num_items + free_space + generation + owner


	item = Suppress('item') + Word(nums)('item')
	itemoff = Suppress('itemoff') + Word(nums)('itemoff')
	itemsize = Suppress('itemsize') + Word(nums)('itemsize')
	parseItemHead = item + key + itemoff + itemsize

	#node 29933568 level 1 items 9 free 484 generation 20 owner 7
	node = Suppress('node') + Word(nums)('node')
	level = Suppress('level') + Word(nums)('level')
	items = Suppress('items') + Word(nums)('items')
	free = Suppress('free') + Word(nums)('free')
	generation = Suppress('generation') + Word(nums)('generation')
	owner = Suppress('owner') + Word(nums)('owner')
	parseNode = node + level + items + free + generation + owner

	#key (EXTENT_CSUM EXTENT_CSUM 136577024) block 29949952 (1828) gen 20
	item = Suppress('key')
	block = Suppress('block') + Word(nums)('block')
	subblock = Suppress('(') + Word(nums)('subblock') + Suppress(')')
	generation = Suppress('gen') + Word(nums)('generation')
	parseNodeKey = item + key + block + subblock + generation

	#inode ref index 2 namelen 10 name: sample.txt
	item = Suppress('inode ref')
	index = Suppress('index') + Word(nums)('index')
	namelen = Suppress('namelen') + Word(nums)('namelen')
	parseInodeRef = item + index + namelen + name


	#inode generation 13 transid 13 size 65536 block group 0 mode 100600 links 1
	item = Suppress('inode')
	generation = Suppress('generation') + Word(nums)('generation')
	transid = Suppress('transid') + Word(nums)('transid')
	size = Suppress('size') + Word(nums)('size')
	block_group = Suppress('block group') + Word(nums)('block_group')
	mode = Suppress('mode') + Word(nums)('mode')
	links = Suppress('links') + Word(nums)('links')
	parseInodeItem = item + generation + transid + size + block_group + mode + links

	#location key (FS_TREE ROOT_ITEM -1) type DIR namelen 7 datalen 0 name: default
	location = Suppress('location')
	typeItem = Suppress('type') + Word(alphas + '_' + '.' + nums)('type')
	namelen = Suppress('namelen') + Word(nums)('namelen')
	datalen = Suppress('datalen') + Word(nums)('datalen')
	parseDirItem = location + key + typeItem + namelen + datalen + name

	#dev extent chunk_tree 3
	#chunk objectid 256 chunk offset 20971520 length 8388608
	item = Suppress('dev extent')
	chunk_tree = Suppress('chunk_tree') + Word(nums)('chunk_tree')
	parseDevExtent = item + chunk_tree

	item = Suppress('chunk')
	objectid = Suppress('objectid') + Word(nums)('chunk_tree')
	chunk_offset = Suppress('chunk offset') + Word(nums)('chunk_offset')
	length = Suppress('length') + Word(nums)('length')
	parseDevExtentChunk = item + objectid + chunk_offset + length


	#prealloc data disk byte 572784640 nr 134217728
	#prealloc data offset 0 nr 134217728
	item = Suppress('prealloc data disk')
	byte = Suppress('byte') + Word(nums)('byte')
	nr = Suppress('nr') + Word(nums)('nr')
	parseExtentDataDisk = item + byte + nr

	item = Suppress('prealloc data offset')
	offset = Suppress('offset') + Word(nums)('offset')
	nr = Suppress('nr') + Word(nums)('nr')
	parseExtentDataOffset = item + offset + nr

	#chunk length 8388608 owner 2 type 1 num_stripes 1
	#stripe 0 devid 1 offset 12582912
	item = Suppress('chunk')
	length = Suppress('length') + Word(nums)('length')
	owner = Suppress('owner') + Word(nums)('owner')
	chunk_type = Suppress('type') + Word(nums)('type')
	num_stripes = Suppress('num_stripes') + Word(nums)('num_stripes')
	parseChunkItem = item + length + owner + chunk_type + num_stripes

	stripe = Suppress('stripe') + Word(nums)('stripe')
	devid = Suppress('devid') + Word(nums)('devid')
	offset = Suppress('offset') + Word(nums)('offset')
	parseChunkItemStripe = stripe + devid + offset

	#dev item devid 1 total_bytes 2145386496 bytes used 470286336
	item = Suppress('dev item')
	devid = Suppress('devid') + Word(nums)('devid')
	total_bytes = Suppress('total_bytes') + Word(nums)('total_bytes')
	bytes_used = Suppress('bytes used') + Word(nums)('bytes_used')
	parseDevItem = item + devid + total_bytes + bytes_used

	item = Word(alphanums)('item')
	tree = Suppress('tree')
	parseTreeHeader_parse = item + tree


	case = {
		'leaf': parseLeaf,
		'item': parseItemHead
	}


	leaf = ''
	node = ""
	k = 0
	file_item = ""

	parfile = enterFile.get()
	path = []
	path.insert(0,"..")
	path.insert(1,parfile)
	
	 


	fs_tree = False
	file_index = -1
	for index, line in enumerate(lines):
		line = line.strip()

		if line.find("fs tree") >= 0:
			fs_tree = True
		if not fs_tree:
			continue

		firstword = line.split(' ')[0] 
		parser = case.get(firstword)

		if parser == None:
			continue

		if firstword == 'item':
			item = parser.parseString(line)

			nextItem = None
			if lines[index + 2].split(' ')[0] == "item":
				nextItem = parser.parseString(lines[index + 2])

			if len(path) == 1 and item['type'] == 'INODE_REF':
				inode_ref = lines[index + 1]
				parseRes = parseInodeRef.parseString(inode_ref)
				if parseRes.name == path[0]:
					file_index = int(index)
			if len(path)  > 1 and item['type'] == 'INODE_REF':
				inode_ref = lines[index + 1]
				parseRes = parseInodeRef.parseString(inode_ref)
				if parseRes.name == path[0]:
					path.remove(path[0])
	

	if file_index < 0:
		return

	lines = lines[file_index:]


	for index, line in enumerate(lines):
		line = line.strip()
		firstword = line.split(' ')[0] 
		parser = case.get(firstword)

		if parser == None:
			continue 

		if firstword == 'item':
			item = parser.parseString(line)

			if item['type'] == 'INODE_REF':
				node = item['item'] + ' ' + item['id'] + ' ' + item['type']  + ' ' + item['itemoff']
				inode_ref = lines[index + 1].strip()
				parseRes = parseInodeRef.parseString(inode_ref)
				node += '\n' + inode_ref

				node = node.replace(":", " - ")

				inode.append(node)

			elif item['type'] == 'EXTENT_DATA':
				node = item['item'] + ' ' + item['id'] + ' ' + item['type']  + ' ' + item['itemoff']
				devext_line = lines[index + 1].strip()
				chunk_line = lines[index + 2].strip()
				node += '\n' + devext_line + '\n' + chunk_line

				node = node.replace(":", " - ")

				inode.append(node)
			else:
				break

def getDisks():
	res = []
	args = ["sudo", "lsblk", "-io", "KNAME,FSTYPE,LABEL,MOUNTPOINT"]
	p = subprocess.Popen(args, stdout=subprocess.PIPE)
	lines, error = p.communicate()
	lines = lines.split('\n')

	kname = Word(alphanums)('kname')
	fstype = Word(alphanums)('fstype')
	label = Word(alphanums)('label')
	mountpoint = Word(alphanums)('mountpoint')
	parser = kname + fstype + Optional(label) + Optional(mountpoint)

	res = []
	for line in lines:
		parsRes = parser.scanString(line)
		for parse in parsRes:
			res.append(parse[0])
	res.remove(res[0])
	return res

def generateGraph():
	G = Graph(
		engine = 'dot',
		filename = 'Btrfs-Graph.dot',
		name = 'BRTFS-Browser',
		comment = 'https://github.com/Zo0MER/BRTFS-Browser.git',
		graph_attr = {'rankdir': 'RL',
						'charset':'utf-8',
						'bgcolor':'#eeeeee',
						'labelloc':'t', 
						'splines':'compound',
						'nodesep':'0.7',
						'ranksep':'5'
					},
		node_attr = {'fontsize': '18.0',
					'shape':'box'
		}
	)

	#node with title and hyperlink on github
	G.node('meta', 
		label = 'Btrfs-debug-tree \nhttps://github.com/Zo0MER/BRTFS-Browser.git', 
		href = 'https://github.com/Zo0MER/BRTFS-Browser.git',
		fontcolor = '#4d2600',
		fontsize = '30.0'
		)

	first = inode[0]
	inode.remove(inode[0])

	if (inode):
		#link first item ROOT_TREE_DIR INODE_ITEM, INODE_REF with all INODE_ITEM EXTEND_DATA
		for pair in inode:
			G.edge(''.join([str(x) for x in first]), ''.join([str(x) for x in pair]))
	else:
		G.node(first)

	#save *.dot and others
	pathout = enterPath.get()
	filenameout = enterFilename.get()

	if (filenameout):
		filenameout = filenameout + '.gv.dot'
	else:
		filenameout = "btrfs-graph"

	G.filename = filenameout + '.gv.dot'
	G.directory = pathout

	G.save()
	for t in types:
		G.format = t
		G.render()



def refreshTypes():
	for pair in checkList:
		checkList[pair].get()
		if (checkList[pair].get()):
			types.append(pair)

def clearTypes():
	del types[:]

def combine(event):
	mainParsing()
	clearTypes()
	refreshTypes()
	generateGraph()


#main window
#create GUI
#
#

root = Tk()

mainFraim = Frame(root, bg = '#FFFFFF')


#Fraim for combine Labels
fraimExtra = Frame(mainFraim, bg = '#ECDBBB')

#text-area to enter btrfs-device name
deviceText = Label(fraimExtra, text = "Enter device name. Example: /dev/sda9", font = "Verdana 12", bg = '#ECDBBB')
deviceText.place(relx = 0.001, rely = 0)
enterDevice = Entry(fraimExtra, width = 30)
enterDevice.place(relx = 0.002, rely = 0.1)

#text-area to enter filename
fileText = Label(fraimExtra, text = "Enter file name. Example: sample.txt", font = "Verdana 12", bg = '#ECDBBB')
fileText.place(relx = 0.001, rely = 0.2)
enterFile = Entry(fraimExtra, width = 30)
enterFile.place(relx = 0.002, rely = 0.3)

#text-area to enter path of output files
pathText = Label(fraimExtra, text = "Enter path for output files. Custom: current directory.", font = "Verdana 12", bg = '#ECDBBB')
pathText.place(relx = 0.001, rely = 0.4)
enterPath = Entry(fraimExtra, width = 30)
enterPath.place(relx = 0.002, rely = 0.5)

#text-area to enter output file(s) name(s)
fileoutText = Label(fraimExtra, text = "Enter name of output file(s). Custom: btrfs-graph.", font = "Verdana 12", bg = '#ECDBBB')
fileoutText.place(relx = 0.001, rely = 0.6)
enterFilename = Entry(fraimExtra, width = 30)
enterFilename.place(relx = 0.002, rely = 0.7)

device = enterDevice.get()
parfile = enterFile.get()
pathout = enterPath.get()
filenameout = enterFilename.get()

fraimExtra.place(relx = 0, rely = 0, relwidth = 0.8, relheight = 0.93)




#checkbutton for choosing type(s) of output file(s)
fraimCheck  = Frame(mainFraim, bg = '#8C794C')

checkinformText = Label(fraimCheck, text = "Chose type(s) of\noutput files", font = "Arial 12", bg = '#8C794C')
checkinformText.pack()

checkList = {}
checkList['pdf'] = BooleanVar()
checkList['svg'] = BooleanVar()
checkList['png'] = BooleanVar()
checkList['imap'] = BooleanVar()
checkList['gd2'] = BooleanVar()

check_1 = Checkbutton(fraimCheck, text = "pdf", variable = checkList['pdf'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_2 = Checkbutton(fraimCheck, text = "svg", variable = checkList['svg'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_3 = Checkbutton(fraimCheck, text = "png", variable = checkList['png'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_4 = Checkbutton(fraimCheck, text = "imap", variable = checkList['imap'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_5 = Checkbutton(fraimCheck, text = "gd2", variable = checkList['gd2'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)

check_2.select()
check_4.select()

check_1.pack()
check_2.pack()
check_3.pack()
check_4.pack()
check_5.pack()



fraimCheck.place(relx = 0.8, rely = 0, relwidth = 0.2, relheight = 0.93)


#define var's for generateGraph()

types = []



#button to start building graph
butStart = Button(mainFraim, font = "Arial 20", bg = '#B5A16A')
butStart.bind("<Button-1>", combine)
butStart["text"] = "Generate Graph"
butStart.place(relx = 0, rely = 0.87, relwidth = 1, relheight = 0.13)



mainFraim.pack(fill = BOTH, expand = 1)


root.minsize(670, 220)
root.maxsize(670, 220)
root.title("BTRFS Graph")
root.mainloop()