#!/usr/bin/env python

import json
import optparse
import sys
import os
import xml.etree.ElementTree as ET
import copy

def xml_large_bbox(xmlstring, outFolder):
	""" read a xml file, and convert the XML string into a python dict """
	
	tree = ET.parse(xmlstring) # import data from the xml file
	root = tree.getroot()

	w = float(root.find('size').find('width').text)
	h = float(root.find('size').find('height').text)

	for obj in root.findall('object'):
		x_list = [] ## x coordinate
		y_list = []

		head_x = float(obj.find('keypoints').find('cent_x').text)
		head_y = float(obj.find('keypoints').find('cent_y').text)
		if(head_x > 0 and head_y > 0):
			x_list.append(head_x)
			y_list.append(head_y)
		Lsho_x = float(obj.find('keypoints').find('left_shoulder_x').text)
		Lsho_y = float(obj.find('keypoints').find('left_shoulder_y').text)
		if(Lsho_x > 0 and Lsho_y > 0):
			x_list.append(Lsho_x)
			y_list.append(Lsho_y)
		Rsho_x = float(obj.find('keypoints').find('right_shoulder_x').text)
		Rsho_y = float(obj.find('keypoints').find('right_shoulder_y').text)
		if(Rsho_x > 0 and Rsho_y > 0):
			x_list.append(Rsho_x)
			y_list.append(Rsho_y)
		neck_x = float(obj.find('keypoints').find('neck_x').text)
		neck_y = float(obj.find('keypoints').find('neck_y').text)
		if(neck_x > 0 and neck_y > 0):
			x_list.append(neck_x)
			y_list.append(neck_y) 

		x_min, y_min, x_max, y_max = w, h, 0, 0
		if(len(x_list) > 0):
			x_min = min(x_list) - 20
			x_max = max(x_list) + 20
			y_min = min(y_list) - 20
			y_max = max(y_list) + 20

		bb_xmin = float(obj.find('bndbox').find('xmin').text)
		bb_ymin = float(obj.find('bndbox').find('ymin').text)
		bb_xmax = float(obj.find('bndbox').find('xmax').text)
		bb_ymax = float(obj.find('bndbox').find('ymax').text)

		obj.find('bndbox').find('xmin').text = str( max( min(bb_xmin, x_min), 0.0) )
		obj.find('bndbox').find('ymin').text = str( max( min(bb_ymin, y_min), 0.0) )
		obj.find('bndbox').find('xmax').text = str( min( max(bb_xmax, x_max), w-1.0) )
		obj.find('bndbox').find('ymax').text = str( min( max(bb_ymax, y_max), h-1.0) )

	print 'write bblarged xml: {}'.format(os.path.join(outFolder, os.path.split(xmlstring)[-1]))
	tree.write(os.path.join(outFolder, os.path.split(xmlstring)[-1]))

def main():
	parser = optparse.OptionParser(
		description='Converts XML files to a single JSON file',
        usage='\n\tpython xml2json.py -o file.json --inFile=1.xml \n\tpython xml2json.py -o file.json --inFolder=xmls/'
		)

	parser.add_option('--inFolder', help="input folder in which have xml files ")
	parser.add_option('--outFolder', help="output folder in which have bbox larged xml files ")
	(options, arguments) = parser.parse_args()
	print arguments

	inFolder = options.inFolder
	outFolder = options.outFolder
	if(os.path.lexists(outFolder)):
		pass
	else:
		os.mkdir(outFolder)

	if inFolder: # input is a folder
		if inFolder[-1] != '/':
			inFolder  = inFolder + '/'
		dirs = os.listdir(inFolder)
		for file in dirs:
			print file
			xml_large_bbox(inFolder + file, outFolder)

if __name__ == "__main__":
	main()