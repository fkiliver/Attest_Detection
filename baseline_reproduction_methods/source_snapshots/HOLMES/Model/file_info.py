# -*- coding: utf-8 -*-
# @Author: Navdha
# @Date:   2020-02-05 20:33:15
# @Last Modified by:   Navdha
# @Last Modified time: 2020-02-07 14:32:23


import os
import copy
import random
import json
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

def preprocess(file):
	# print("file33333",file)
	f = open(file,"r")
	contents = f.read()
	vertices = []
	edges = []
	components = contents.split("\n")

	for component in components:
		if( component[:6] == "vertex"):
			vertices.append(component[7:])
		elif( component[:4] == "edge"):
			edges.append(component[5:])

	matrix = edgedependence(vertices, edges)
	encode = hotencode(vertices, edges)	
	return matrix, encode


def hotencode(vertices, edges):
	statement_type = []
	for vertex in vertices:
		vertex_dict = json.loads(vertex)
		statement_type.append(vertex_dict['unit_type'])

	statements = ['NULL','AssignStmt','DefinitionStmt','IdentityStmt','IfStmt','ReturnStmt','BreakpointStmt','EnterMonitorStmt' , 'ExitMonitorStmt' , 'GotoStmt','InvokeStmt' , 'LookupSwitchStmt' , 'MonitorStmt','NopStmt' , 'RetStmt' , 'ReturnVoidStmt','TableSwitchStmt' , 'ThrowStmt']
	encode = np.zeros((len(statement_type),len(statements)), dtype = 'int32')
	s_index = 0
	for s in statement_type:
		stmt_index = 0
		for stmt in statements:
			if (stmt in s):
				encode[s_index][stmt_index] = 1
				break
			stmt_index += 1
		s_index += 1

	return encode

def edgedependence(vertices, edges):
	matrix = np.empty((2,0), dtype = 'int32')

	for edge in edges:
		edge_dict = json.loads(edge)
		label = str(edge_dict["label"])
		a = edge_dict['src']
		b = edge_dict['targ']

		matrix = np.append(matrix, [[a],[b]], axis = 1)

	return matrix
