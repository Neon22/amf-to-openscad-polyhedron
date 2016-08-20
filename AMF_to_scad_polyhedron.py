#!/usr/bin/python
from __future__ import print_function

### Convert the AMF format (xml based) into the point/polygon form for OpenSCAD
### usual use case is:
# 1. create object in openSCAD
# 2. want to have a polyhedron version
# 3. so export as AMF and convert to polyhedrons using this program
# 4. Load it back in by cutting and pasting the three lines per mesh into your openSCAD file.


import sys
import os.path


# manual file defined
filename = "Test.amf"
invert_faces = True # if the resulting object is inside out (F12 shows pink), then swap this.

#=================================
def extract_block(lines, blockstart, blockend):
	" collect the lines between the block labels "
	data = []
	current = []
	gathering = False
	idx = 0
	for line in lines:
		if line.find(blockstart) >= 0:
			gathering = True
		if gathering:
			current.append(line)
		if line.find(blockend) >= 0:
			gathering = False
			data.append(current)
			current = []
	return data

def parse_vertices(lines):
	" look for the X,Y,Z tagged lines and assemble into triplets"
	vertices = []
	triplet = []
	count = 0
	possibles = ["<x>", "<y>","<z>"]
	while count < len(lines):
		line = lines[count]
		for tag in possibles:
			start = line.find(tag)
			if start >= 0:
				triplet.append(line[start+len(tag):line.find("</")])
		if len(triplet) == 3:
			vertices.append(triplet)
			triplet = []
		count += 1
	return vertices

def parse_triplets(lines, tags=["<v1>", "<v2>","<v3>"]):
	" look for the X,Y,Z tagged lines and assemble into triplets"
	elements = []
	triplet = []
	count = 0
	while count < len(lines):
		line = lines[count]
		for tag in tags:
			start = line.find(tag)
			if start >= 0:
				triplet.append(line[start+len(tag):line.find("</")])
		if len(triplet) == 3:
			elements.append(triplet)
			triplet = []
		count += 1
	return elements

def create_polygons(verts, tris, index):
	" take string data and prepare for output "
	# result = []
	point_label = "points_%d" % (index)
	face_label =  "triangles_%d" % (index)
	#
	points = "%s=[" %(point_label)
	for x,y,z in verts:
		points += "["+x+","+y+","+z+"],"
	points = points[:-1]+"];"
	faces = "%s=[" %(face_label)
	for a,b,c in tris:
		if invert_faces: a,c = c,a # swap order
		faces += "["+a+","+b+","+c+"],"
	faces = faces[:-1]+"];"
	polyhedron = "polyhedron(" + point_label + "," + face_label + ");"
	return [points, faces, polyhedron]

def parse_file(file):
	" "
	lines = file.readlines()
	meshes = extract_block(lines, "<mesh", "</mesh")
	print("Found", len(meshes), "mesh.")
	polygons = []
	mesh_idx = 0
	for mesh in meshes:
		vertice_data = extract_block(mesh, "<vertices", "</vertices")[0]
		vertices = parse_triplets(vertice_data, ["<x>", "<y>","<z>"])
		triangle_data = extract_block(mesh, "<volume", "</volume")[0]
		triangles = parse_triplets(triangle_data, ["<v1>", "<v2>","<v3>"])
		print(" Found",len(vertices), "vertices and", len(triangles), "triangles.")
		print (vertices,"\n",triangles)
		polygons.append(create_polygons(vertices, triangles, mesh_idx))
		mesh_idx += 1
	return polygons



def write_openscad_polygons(filename, data):
	" "
	print(filename, data)
	outf = open(filename, 'w')
	count = 0
	for mesh in data:
		name = "Object_"+str(count)
		verts, faces, polyhedron = mesh
		outf.write(verts+"\n")
		outf.write(faces+"\n")
		outf.write(polyhedron+"\n")
	outf.close()



if __name__ == "__main__":
	# did we get an AMF  file dropped on us
	if len(sys.argv) == 2:
		# got an argument - is it an AMF
		filename = sys.argv[1]
	if len(sys.argv) == 1:
		# called on its own
		pass
	else:
		# too many args
		print("Usage: just drop one AMF file on top")
		filename = ''
	#
	if filename: # (dropped or manually set)
		inf = open(filename, 'rU')
		data = parse_file(inf)
		first,ext = os.path.splitext(filename)
		first += '_convert'
		newfilename = first+'.scad'
		write_openscad_polygons(newfilename, data)
		inf.close()
