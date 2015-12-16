from graphviz import Digraph
from pyparsing import *
import sys
import os
import subprocess


lines = ""
if len(sys.argv) > 1:
	args = ["sudo", "btrfs-debug-tree"]
	args.extend(sys.argv[1:])
	p = subprocess.Popen(args, stdout=subprocess.PIPE)
	lines, error = p.communicate()
	lines = lines.splitlines(True)
else:
	sys.exit()



def parseLeaf(data):
	leaf = Suppress('leaf') + Word(nums)('leaf')
	num_items = Suppress('items') + Word(nums)('items')
	free_space = Suppress('free space') + Word(nums)('free_space')
	generation = Suppress('generation') + Word(nums)('generation')
	owner = Suppress('owner') + Word(nums)('owner')
	parse_module = leaf + num_items + free_space + generation + owner
	res = parse_module.parseString(data)
	return res

def parseItemHead(data):
	item = Suppress('item') + Word(nums)('item')
	key = Suppress('key (') +  Word(alphas + '_' + nums)('id') + Word(alphas + '_' + nums)('type') + \
		Word(alphas + '_' + nums)('offset') + Suppress(')')
	itemoff = Suppress('itemoff') + Word(nums)('itemoff')
	itemsize = Suppress('itemsize') + Word(nums)('itemsize')
	parse_module = item + key + itemoff + itemsize
	res = parse_module.parseString(data)
	return res

def parseNode(data):
	node = Suppress('node') + Word(nums)('node')
	level = Suppress('level') + Word(nums)('level')
	items = Suppress('items') + Word(nums)('items')
	free = Suppress('free') + Word(nums)('free')
	generation = Suppress('generation') + Word(nums)('generation')
	owner = Suppress('owner') + Word(nums)('owner')
	parse_module = node + level + items + free + generation + owner
	res = parse_module.parseString(data)
	return res

def parseNodeKey(data):
	item = Suppress('key')
	key = Suppress('key (') +  Word(alphas + '_' + nums)('id') + Word(alphas + '_' + nums)('type') + \
		Word(alphas + '_' + nums)('offset') + Suppress(')')
	block = Suppress('block') + Word(nums)('block')
	subblock = Suppress('(') + Word(nums)('subblock') + Suppress(')')
	generation = Suppress('gen') + Word(nums)('generation')
	parse_module = item + key + block + subblock + generation
	res = parse_module.parseString(data)
	return res

#inode ref index 2 namelen 10 name: sample.txt
def parseInodeRef(data):
	item = Suppress('inode ref')
	index = Suppress('index') + Word(nums)('index')
	namelen = Suppress('namelen') + Word(nums)('namelen')
	name = Suppress('name:') + Word(alphanums + '.' + '_')('name')
	parse_module = item + index + namelen + name
	res = parse_module.parseString(data)
	return res

#inode generation 13 transid 13 size 65536 block group 0 mode 100600 links 1
def parseInodeItem(data):
	item = Suppress('inode')
	generation = Suppress('generation') + Word(nums)('generation')
	transid = Suppress('transid') + Word(nums)('transid')
	size = Suppress('size') + Word(nums)('size')
	block_group = Suppress('block group') + Word(nums)('block_group')
	mode = Suppress('mode') + Word(nums)('mode')
	links = Suppress('links') + Word(nums)('links')
	parse_module = item + generation + transid + size + block_group + mode + links
	res = parse_module.parseString(data)
	return res

#location key (258 INODE_ITEM 0) type FILE
#namelen 13 datalen 0 name: sample{i}.txt	
def parseDirItem(data):
	item = Suppress('inode')
	key = Suppress('key (') +  Word(alphas + '_' + nums)('id') + Word(alphas + '_' + nums)('type') + \
		Word(alphas + '_' + nums)('offset') + Suppress(')')
	typeItem = Suppress('type') + Word(alphas + '_' + '.' + nums)('type')
	parse_module = item + key + transid + typeItem
	res = parse_module.parseString(data)
	return res

#dev extent chunk_tree 3
#chunk objectid 256 chunk offset 20971520 length 8388608
def parseDevExtent(data):
	item = Suppress('dev extent')
	chunk_tree = Suppress('chunk_tree') + Word(nums)('chunk_tree')
	parse_module = item + chunk_tree
	res = parse_module.parseString(data)
	return res
def parseDevExtentChunk(data):
	item = Suppress('chunk')
	objectid = Suppress('objectid') + Word(nums)('chunk_tree')
	chunk_offset = Suppress('chunk offset') + Word(nums)('chunk_offset')
	length = Suppress('length') + Word(nums)('length')
	parse_module = item + objectid + chunk_offset + length
	res = parse_module.parseString(data)
	return res

#prealloc data disk byte 572784640 nr 134217728
#prealloc data offset 0 nr 134217728
def parseExtentDataDisk(data):
	item = Suppress('prealloc data disk')
	byte = Suppress('byte') + Word(nums)('byte')
	nr = Suppress('nr') + Word(nums)('nr')
	parse_module = item + byte + nr
	res = parse_module.parseString(data)
	return res
def parseExtentDataOffset(data):
	item = Suppress('prealloc data offset')
	offset = Suppress('offset') + Word(nums)('offset')
	nr = Suppress('nr') + Word(nums)('nr')
	parse_module = item + offset + nr
	res = parse_module.parseString(data)
	return res

#chunk length 8388608 owner 2 type 1 num_stripes 1
#stripe 0 devid 1 offset 12582912
def parseChunkItem(data):
	item = Suppress('chunk')
	length = Suppress('length') + Word(nums)('length')
	owner = Suppress('owner') + Word(nums)('owner')
	chunk_type = Suppress('type') + Word(nums)('type')
	num_stripes = Suppress('num_stripes') + Word(nums)('num_stripes')
	parse_module = item + length + owner + chunk_type + num_stripes
	res = parse_module.parseString(data)
	return res
def parseChunkItemStripe(data):
	stripe = Suppress('stripe') + Word(nums)('stripe')
	devid = Suppress('devid') + Word(nums)('devid')
	offset = Suppress('offset') + Word(nums)('offset')
	parse_module = stripe + devid + offset
	res = parse_module.parseString(data)
	return res

#dev item devid 1 total_bytes 2145386496 bytes used 470286336
def parseDevItem(data):
	item = Suppress('dev item')
	devid = Suppress('devid') + Word(nums)('devid')
	total_bytes = Suppress('total_bytes') + Word(nums)('total_bytes')
	bytes_used = Suppress('bytes used') + Word(nums)('bytes_used')
	parse_module = item + devid + total_bytes + bytes_used
	res = parse_module.parseString(data)
	return res

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

items = []
inode = []

dot = Digraph(engine='neato', graph_attr={'rankdir': 'LR'}, node_attr = {'fontsize': '8'})

for index, line in enumerate(lines):
	line = line.strip()
	func = case.get(line.split(' ')[0])

	if func == None:
		continue 

	firstword = line.split(' ')[0] 
	#if firstword == 'leaf':
		#if leaf != '':
		#leaf = func(line)
		#items = "leaf " + leaf['leaf'] + ' ' + leaf['owner']
	if firstword == 'item':
		#items += " | "
		item = func(line)
		#if item['type'] == 'DEV_EXTENT':
		#	devext_line = lines[index + 1].strip()
		#	chunk_line = lines[index + 2].strip()
		#	parseDevExtent(devext_line)
		#	parseDevExtentChunk(chunk_line)
		#if item['type'] == 'CHUNK_ITEM':
		#	chunk_line = lines[index + 1].strip()
		#	chunkitem = parseChunkItem(chunk_line)
		#	stripes = []
		#	for strip_index in xrange(int(chunkitem.num_stripes)):
		#		strip_line = lines[index + strip_index + 2].strip()
		#		stripes.append(parseChunkItemStripe(strip_line))
		#	item['stripes'] = stripes
		#if item['type'] == 'DEV_ITEM':
		#	item_line = lines[index + 1].strip()
		#	parseDevItem(item_line)
		if item['type'] == 'EXTENT_DATA':
			node = item['item'] + ' ' + item['id'] + ' ' + item['type']  + ' ' + item['itemoff']
			devext_line = lines[index + 1].strip()
			chunk_line = lines[index + 2].strip()
			node += '\n' + devext_line + '\n' + chunk_line
		#	extentDataDisk = parseExtentDataDisk(devext_line)
		#	extentDataOffset = parseExtentDataOffset(chunk_line)
			dot.node('node' + str(k) , node, shape = 'record')
			k += 1
			dot.edge(file_item, 'node' + str(k), constraint='false')

		if item['type'] == 'INODE_ITEM':
			node = item['item'] + ' ' + item['id'] + ' ' + item['type']  + ' ' + item['itemoff']
			inode_item = lines[index + 1].strip()
			node += '\n' + inode_item
			file_item = 'node' + str(k)
			dot.node('node' + str(k) , node, shape = 'record')
			k += 1
			
		if item['type'] == 'INODE_REF':
			node = item['item'] + ' ' + item['id'] + ' ' + item['type']  + ' ' + item['itemoff']
			inode_ref = lines[index + 1].strip()
			node += '\n' + inode_ref
			dot.node('node' + str(k) , node, shape = 'record')
			k += 1
			dot.edge(file_item, 'node' + str(k), constraint='false')

	#if firstword == 'node':
	#	items += " | "
	#	item = func(line)
	#	items += item['item'] + ' ' + item['id'] + ' ' + item['type']  + ' ' + item['itemoff']

dot.view()
#dot.edge('B:f0', 'L', constraint='false')