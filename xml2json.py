#!/usr/bin/env python

import json
import optparse
import sys
import os
import xml.etree.ElementTree as ET
import copy

annolist_index = 0.0

def xml2dict(xmlstring, anno_list):
	""" read a xml file, and convert the XML string into a python dict """
	
	tree = ET.parse(xmlstring) # import data from the xml file
	root = tree.getroot()

	xml_dict = {} # store the data of xml file, which is same for all object in the same image
	xml_dict['folder'] = root.find('folder').text
	xml_dict['img_paths'] = xmlstring.split('.')[0] + '.jpg'
	xml_dict['source'] = {}
	xml_dict['source']['database'] = root.find('source').find('database').text
	xml_dict['source']['annotation'] = root.find('source').find('annotation').text
	xml_dict['owner_name'] = root.find('owner').find('name').text
	xml_dict['img_width'] = float(root.find('size').find('width').text)
	xml_dict['img_height'] = float(root.find('size').find('height').text)
	xml_dict['depth'] = float(root.find('size').find('depth').text)
	xml_dict['segmented'] = float(root.find('segmented').text)
	xml_dict['isValidation'] = 0.0
	xml_dict['dataset'] = 'Undef'
	xml_dict['numOtherPeople'] = len(root.findall('object')) - 1

	global annolist_index
	annolist_index = annolist_index + 1.0
	xml_dict['annolist_index'] = annolist_index

	people_index = 0.0
	obj_dict_list = [] # store all obj_dicts in one image 
	for obj in root.findall('object'):
		obj_dict = copy.deepcopy(xml_dict)
		people_index = people_index + 1.0
		obj_dict['people_index'] = people_index
		obj_dict['object_name'] = obj.find('name').text
		obj_dict['pose'] = obj.find('pose').text
		obj_dict['truncated'] = float(obj.find('truncated').text)
		obj_dict['difficult'] = float(obj.find('difficult').text)
		obj_dict['occluded'] = float(obj.find('occluded').text)
		obj_dict['confidence'] = float(obj.find('confidence').text)

		obj_dict['bbox'] = []
		obj_dict['bbox'].append( float(obj.find('bndbox').find('xmin').text) )
		obj_dict['bbox'].append( float(obj.find('bndbox').find('ymin').text) )
		obj_dict['bbox'].append( float(obj.find('bndbox').find('xmax').text) - float(obj.find('bndbox').find('xmin').text) )
		obj_dict['bbox'].append( float(obj.find('bndbox').find('ymax').text) - float(obj.find('bndbox').find('ymin').text) )
		obj_dict['objpos'] = []
		obj_dict['objpos'].append( (float(obj.find('bndbox').find('xmax').text) + float(obj.find('bndbox').find('xmin').text))/2.0 )
		obj_dict['objpos'].append( (float(obj.find('bndbox').find('ymax').text) + float(obj.find('bndbox').find('ymin').text))/2.0 )

		obj_dict['num_keypoints'] = 4
		obj_dict['joint_self'] = []
		if obj_dict['numOtherPeople'] > 1:
			obj_dict['joint_others'] = []
			obj_dict['objpos_other'] = []
			obj_dict['scale_provided_other'] = []
		obj_dict['scale_provided'] = 1.0 # no provided, here is a default value
		keypoint = []
		for child in obj.find('keypoints'):
			keypoint.append( float(child.text) )
			#obj_dict['keypoints'].append( float(child.text) )
			if child.tag[-1] == 'y':
				keypoint.append(1) # visiable flag
				obj_dict['joint_self'].append(copy.deepcopy(keypoint))
				keypoint = []

		#anno_list.append( copy.deepcopy(obj_dict) )
		obj_dict_list.append( copy.deepcopy(obj_dict) )
		obj_dict.clear()

	for i in range( len(obj_dict_list) ):
		for j in range( len(obj_dict_list) ):
			if j != i:
				if obj_dict_list[i]['numOtherPeople'] > 1:
					obj_dict_list[i]['joint_others'].append( copy.deepcopy(obj_dict_list[j]['joint_self']) )
					obj_dict_list[i]['objpos_other'].append( copy.deepcopy(obj_dict_list[j]['objpos']) )
					obj_dict_list[i]['scale_provided_other'].append( copy.deepcopy(obj_dict_list[j]['scale_provided']) )
				else:
					obj_dict_list[i]['joint_others'] = copy.deepcopy(obj_dict_list[j]['joint_self'])
					obj_dict_list[i]['objpos_other'] = copy.deepcopy(obj_dict_list[j]['objpos'])
					obj_dict_list[i]['scale_provided_other'] = copy.deepcopy(obj_dict_list[j]['scale_provided'])
		anno_list.append( copy.deepcopy(obj_dict_list[i]) )


def main():
	parser = optparse.OptionParser(
		description='Converts XML files to a single JSON file',
        usage='\n\tpython xml2json.py -o file.json --inFile=1.xml \n\tpython xml2json.py -o file.json --inFolder=xmls/'
		)
	parser.add_option('-o', '--output', help="out file name")
	parser.add_option('--inFile', help="input xml filename ")
	parser.add_option('--inFolder', help="input folder in which have xml files ")
	(options, arguments) = parser.parse_args()
	print arguments

	jsonFile = options.output

	anno_list = [] # annotation list, have the same format as COCO dataset 

	inFile = options.inFile
	inFolder = options.inFolder

	if inFile: # input is a single xml file
		xml2dict(inFile, anno_list)

	if inFolder: # input is a folder
		if inFolder[-1] != '/':
			inFolder  = inFolder + '/'
		dirs = os.listdir(inFolder)
		for file in dirs:
			print file
			xml2dict(inFolder + file, anno_list)

	json_data = json.dumps(anno_list, indent=4)
	if(jsonFile):
		fileWriter = open(jsonFile, 'w')
		fileWriter.write(json_data)
		fileWriter.close()
	else:
		print(json_data) 

if __name__ == "__main__":
	main()