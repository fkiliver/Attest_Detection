# -*- coding: utf-8 -*-
# @Author: Navdha
# @Date:   2020-05-18 14:36:40
# @Last Modified by:   Navdha
# @Last Modified time: 2020-05-18 14:39:46


import os
import copy
import random
import json
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

def preprocess(file):
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

	mat_data, mat_control = edgedependence(vertices, edges)
	encode = hotencode(vertices, edges)	
	return mat_data, mat_control, encode


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

	return encode.tolist()

def edgedependence(vertices, edges):
	mat_data = np.empty((2,0), dtype = 'int32')
	mat_control = np.empty((2,0), dtype = 'int32')
	for edge in edges:
		edge_dict = json.loads(edge)
		label = str(edge_dict["label"])
		a = edge_dict['src']
		b = edge_dict['targ']

		if (label == ""):
			mat_control = np.append(mat_control, [[a],[b]], axis = 1)
		else:
			mat_data = np.append(mat_data, [[a],[b]], axis = 1)

	return mat_data.tolist(), mat_control.tolist()
