#!/usr/bin/env python

import sys
import struct
import json
import collections
import itertools

import rs5file

data_types = collections.OrderedDict()
json_decoders = {}
def data_type(c):
	global data_types
	data_types[c.id] = c
	if hasattr(c, 'from_json'):
		json_decoders[c.id] = c
	return c

def parse_type(t, f):
	c = data_types[t]
	if hasattr(c, 'dec_new'):
		return c.dec_new(f)
	r = c()
	r.dec(f)
	return r

def encode_json_types(obj):
	return obj.to_json()

def decode_json_types(dct):
	ret = collections.OrderedDict()
	for (k,v) in dct:
		assert(k[1] == ':')
		if k[0] in json_decoders:
			r = json_decoders[k[0]]()
			r.from_json(v)
			ret[null_str(k)] = r
		else:
			ret[null_str(k)] = v
	# print ret
	return ret

def dump_json(node, outputfd):
	return json.dump(node, outputfd, default=encode_json_types, ensure_ascii=True, indent=4, separators=(',', ': '))
def dumps_json(node):
	return json.dumps(node, default=encode_json_types, ensure_ascii=True, indent=4, separators=(',', ': '))
def dumps_json_node(node):
	return json.dumps((node.id, node), default=encode_json_types, ensure_ascii=True, separators=(',', ': '))

def parse_json(j):
	j = json.load(j, object_pairs_hook=decode_json_types, parse_int=data_int, parse_float=data_float)
	root = data_tree()
	root.from_json(j)
	return root
def parse_json_node(j):
	(type, node) = json.loads(j, object_pairs_hook=decode_json_types, parse_int=data_int, parse_float=data_float)
	if type in json_decoders:
		r = json_decoders[type]()
		r.from_json(node)
		return r
	return data_types[type](node)

@data_type
class data_null(object):
	id = '.'
	desc = 'NULL'
	def dec(self, f):
		pass
	def to_json(self):
		return None
	def from_json(self, j):
		pass
	def enc(self):
		return ''
	def __eq__(self, other):
		return other == None
	def __ne__(self, other):
		return other != None
	def __str__(self):
		return '<NULL>'

@data_type
class null_str(str):
	id = 's'
	desc = 'String'
	@classmethod
	def dec_new(cls, f=''):
		r = ''
		while True:
			c = f.read(1)
			if c == '\0':
				# print>>sys.stderr, 'string: '+r
				return str.__new__(cls, r)
			r += c
	def enc(self):
		return self + '\0'

@data_type
class data_tree(object):
	id = 'T'
	desc = 'Tree Node'
	def __init__(self, *args):
		self.children = collections.OrderedDict(args)
		for (name, child) in self.children.iteritems():
			child.parent = self
			child.name = name
		self.parent = None
		self.name = None
	def dec(self, f):
		while True:
			name = null_str.dec_new(f)
			if name == '':
				break
			t = f.read(1)
			try:
				child = parse_type(t, f)
				self[name] = child
			except:
				dump_json(self.children, sys.stderr)
				raise
	def to_json(self):
		r = collections.OrderedDict()
		for (name, child) in self.iteritems():
			r['%s:%s' % (child.id, name)] = child
		return r
	def from_json(self, c):
		for (name, child) in c.iteritems():
			if isinstance(child, unicode):
				child = null_str(child)
			self[null_str(name[2:])] = child
	def enc(self):
		ret = ''
		for (name, child) in self.iteritems():
			try:
				ret += name.enc() + child.id + child.enc()
			except:
				print name, type(name), child
				raise
		return ret + '\0'

	def expand_tree(self):
		ret = [self]
		for child in self.itervalues():
			if isinstance(child, data_tree):
				ret.extend(child.expand_tree())
			else:
				ret.append(child)
		return ret

	def diff(self, other):
		def expand_node(node):
			if isinstance(node, data_tree):
				return node.expand_tree()
			return [node]

		my_children = set(self.children)
		other_children = set(other.children)

		added = [ (parent_list(other[child]), other[child]) \
				for child in other_children.difference(my_children) ]
		removed = [ parent_list(self[child]) \
				for child in my_children.difference(other_children) ]

		changed = []
		for child in my_children.intersection(other_children):
			my_child = self[child]
			other_child = other[child]
			if type(my_child) != type(other_child):
				changed.append( (parent_list(other_child), other_child) )
			elif isinstance(my_child, data_tree):
				(a, r, c) = my_child.diff(other_child)
				added.extend(a)
				removed.extend(r)
				changed.extend(c)
			elif my_child != other_child:
				changed.append( (parent_list(other_child), other_child) )
		return (added, removed, changed)


	def __getitem__(self, item):
		return self.children[item]

	def __iter__(self): return iter(self.children)
	def keys(self): return self.children.keys()
	def values(self): return self.children.values()
	def items(self): return self.children.items()
	def iterkeys(self): return self.children.iterkeys()
	def itervalues(self): return self.children.itervalues()
	def iteritems(self): return self.children.iteritems()
	def __len__(self): return len(self.children)
	def __getitem__(self, item): return self.children[item]
	def __setitem__(self, item, val):
		val.name = item
		val.parent = self
		self.children[item] = val
	def __delitem__(self, item): del self.children[item]

def parent_list(node, skip=0):
	if node.parent:
		ret = parent_list(node.parent)
		if isinstance(ret, int):
			if ret < 0:
				return ret+1
			return [node.name]
		return ret + [node.name]
	return -skip

def format_parent(node, skip=0):
	return '.'.join(parent_list(node, skip))

@data_type
class data_int(int):
	id = 'i'
	desc = 'Integer'
	@classmethod
	def dec_new(cls, f = 0):
		return int.__new__(cls, struct.unpack('<i', f.read(4))[0])
	def enc(self):
		return struct.pack('<i', self)

@data_type
class data_float(float):
	id = 'f'
	desc = 'Floating Point Number'
	@classmethod
	def dec_new(cls, f = 0.0):
		return float.__new__(cls, struct.unpack('<f', f.read(4))[0])
	def enc(self):
		return struct.pack('<f', self)

class data_list(object):
	def __init__(self):
		self.list = []
	def dec(self, f):
		self.len = data_int.dec_new(f)
		for i in range(self.len):
			e = self.parse(f)
			self.list.append(e)
	def enc(self):
		r = self.len.enc()
		for i in self.list:
			r += i.enc()
		return r
	def to_json(self):
		return self.list

	def from_json(self, l):
		for i in l:
			if isinstance(i, unicode):
				i = null_str(i)
			self.list.append(i)
		self.len = data_int(len(l))

	def __iter__(self): return iter(self.list)
	def __getitem__(self, item): return self.list[item]
	def __setitem__(self, item, val): self.list[item] = val
	def __delitem__(self, item): del self.list[item]
	def insert(self, index, object):
		return self.list.insert(index, object)
	def remove(self, item):
		self.list.remove(item)
		self.len = data_int(len(self.list))
	def __len__(self): return len(self.list)

	def summary(self):
		if len(self.list) > 5:
			return ', '.join(map(str, self.list[:5]) + ['...'])
		return ', '.join(map(str, self.list))

	def __str__(self):
		return ', '.join(map(str, self.list))
	def __eq__(self, other):
		return self.list == other.list
	def __ne__(self, other):
		return self.list != other.list

@data_type
class data_int_list(data_list):
	id = 'I'
	desc = 'List of Integers'
	type = data_int
	parse = data_int.dec_new

@data_type
class data_str_list(data_list):
	id = 'S'
	desc = 'List of Strings'
	type = null_str
	parse = null_str.dec_new

@data_type
class data_float_list(data_list):
	id = 'F'
	desc = 'List of Floats'
	type = data_float
	parse = data_float.dec_new

@data_type
class data_mixed_list(data_list):
	id = 'M'
	desc = 'Mixed type List'
	@staticmethod
	def parse(f):
		t = f.read(1)
		return parse_type(t, f)
	def enc(self):
		r = self.len.enc()
		for i in self.list:
			r += i.id + i.enc()
		return r

@data_type
class data_raw(object):
	id = 'R'
	desc = 'Raw Binary Data'
	def __init__(self):
		self.raw = ''
	def dec(self, f):
		l = data_int.dec_new(f)
		self.raw = f.read(l)
	def enc(self):
		return data_int(len(self.raw)).enc() + self.raw
	def to_json(self):
		return self.raw.encode('hex_codec')
	def from_json(self, l):
		self.raw = l.decode('hex_codec')
	def summary(self):
		r = self.raw[:32]
		ret = ' '.join(['%.2x' % ord(x) for x in r])
		if r == self.raw:
			return ret
		return ret + '...'
	def __str__(self):
		return ' '.join(['%.2x' % ord(x) for x in self.raw])
	def __eq__(self, other):
		return self.raw == other.raw
	def __ne__(self, other):
		return self.raw != other.raw

def diff_data(tree1, tree2):
	(added, removed, changed) = tree1.diff(tree2)
	return {'added': added, 'removed': removed, 'changed': changed}

def apply_diff(root, diff):
	def find_parent_node(plist):
		node = root
		for name in plist[:-1]:
			node = node[name]
			if not isinstance(node, data_tree):
				raise TypeError('%s is not a tree node' % name)
		return node

	for plist in diff['removed']:
		try:
			parent = find_parent_node(plist)
			del parent[plist[-1]]
		except (KeyError, ValueError):
			raise # XXX: For testing
			continue
	for (plist, node) in sorted(itertools.chain(diff['added'], diff['changed'])):
		assert type(node) in data_types.values()
		try:
			parent = find_parent_node(plist)
		except (KeyError, ValueError):
			raise # XXX: For testing
			continue
		name = null_str(plist[-1])
		parent[name] = node

def json_encode_diff(diff, outputfd):
	tmp = diff.copy()
	tmp['added']   = [ (plist, dumps_json_node(node)) for (plist, node) in diff['added'] ]
	tmp['changed'] = [ (plist, dumps_json_node(node)) for (plist, node) in diff['changed'] ]

	json.dump(tmp, outputfd, indent=4)

def json_decode_diff(inputfd):
	diff = json.load(inputfd)
	diff['added']   = [ (plist, parse_json_node(j)) for (plist, j) in diff['added'] ]
	diff['changed'] = [ (plist, parse_json_node(j)) for (plist, j) in diff['changed'] ]
	return diff

def pretty_print_diff(diff):
	removed = itertools.izip_longest(diff['removed'], [], fillvalue=None)
	removed = itertools.izip_longest(removed, [], fillvalue='-')
	added = itertools.izip_longest(diff['added'], [], fillvalue='+')
	changed = itertools.izip_longest(diff['changed'], [], fillvalue='>')
	combined = sorted(itertools.chain(added, removed, changed))

	for ((plist, node), prefix) in combined:
		if node is not None:
			print '%s %s: %s' % (prefix, '->'.join(plist), dumps_json(node))
		else:
			print '%s %s' % (prefix, '->'.join(plist))

def parse_data(f):
	try:
		t = f.read(1)
		return parse_type(t, f)
	except:
		print 'Address: 0x%x' % f.tell()
		raise

def data2json(f, outputfd):
	return dump_json(parse_data(f), outputfd)

def parse_chunk(chunk):
	assert(chunk.name == 'DATA')
	return parse_data(chunk.get_fp())

def chunk2json(chunk, outputfd):
	assert(chunk.name == 'DATA')
	return data2json(chunk.get_fp(), outputfd)

def encode(root):
	return root.id + root.enc()

def json2data(j):
	root = parse_json(j)
	return encode(root)

def write_data(j, outputfd):
	outputfd.write(json2data(j))

def make_chunk(data):
	return rs5file.Rs5ChunkEncoder('DATA', data)

def parse_args():
	import argparse
	parser = argparse.ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-d', '--decode-file', metavar='FILE',
			type=argparse.FileType('rb'),
			help='Decode a previously extracted database')
	group.add_argument('-e', '--encode-file', metavar='FILE',
			type=argparse.FileType('rb'),
			help='Encode a JSON formatted database')

	parser.add_argument('-o', '--output',
			type=argparse.FileType('wb'), default=sys.stdout,
			help='Store the result in OUTPUT')

	return parser.parse_args()


class MiasmataDataType(object):
	class meta(type):
		def __instancecheck__(self, instance):
			return instance.__class__ in data_types.values()
		def __subclasscheck__(self, cls):
			return cls in data_types.values()
	__metaclass__ = meta

class MiasmataDataCoercible(object):
	coercible = null_str, data_int, data_float
	class meta(type):
		def __instancecheck__(self, instance):
			return instance.__class__ in self.coercible
		def __subclasscheck__(self, cls):
			return cls in self.coercible
	__metaclass__ = meta

def main():
	args = parse_args()

	if args.decode_file:
		return data2json(args.decode_file, args.output)

	if args.encode_file:
		return write_data(args.encode_file, args.output)

if __name__ == '__main__':
	main()
