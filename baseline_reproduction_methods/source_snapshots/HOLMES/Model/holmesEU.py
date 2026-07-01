import os.path as osp, os
from ast import literal_eval
import numpy as np, pandas as pd
from torch_geometric.nn import GATConv,SAGPooling,GCNConv,JumpingKnowledge, GlobalAttention, global_mean_pool as gap, global_max_pool as gmp
from torch_geometric.data import Dataset, Data, DataLoader
import torch.nn.functional as F, torch.nn as nn, torch
import torchvision

layer_num = 4
lstmHidden = 100
loss_op = nn.BCEWithLogitsLoss()


class Breadth(torch.nn.Module):
	def __init__(self, in_dim, out_dim):
		super(Breadth, self).__init__()
		self.conv1 = GATConv(in_dim, out_dim, heads = 4)
		self.lin1 = nn.Linear(in_dim,out_dim*4)
		self.conv3 = GATConv(4 * in_dim, out_dim, heads=6, concat=False)
		self.lin3 = torch.nn.Linear(4 * in_dim, out_dim)

	def forward(self, x, edge_index):
		x = F.leaky_relu(self.conv1(x, edge_index) + self.lin1(x))
		x = F.leaky_relu(self.conv3(x, edge_index) + self.lin3(x))
		return x

class Depth(torch.nn.Module):
	def __init__(self, in_dim, lstm_hidden):
		super(Depth, self).__init__()
		self.lstm = nn.LSTM(in_dim, lstm_hidden, 1, bias=False)
	def forward(self, x,h,c):
		x, (h, c) = self.lstm(x, (h, c))
		return x,(h,c)

class HolmesLayer(torch.nn.Module):
	def __init__(self, in_dim):
		super(HolmesLayer, self).__init__()
		self.breadth_func = Breadth(in_dim, in_dim)
		self.depth_func = Depth(in_dim, lstmHidden)

	def forward(self, x, edge_index,h,c):
		x = self.breadth_func(x, edge_index)
		x = x[None, :]
		x, (h,c) = self.depth_func(x,h,c)
		x = x[0]
		return x, (h,c)


class Holmes(torch.nn.Module):
	def __init__(self, in_dim):
		super(Holmes, self).__init__()
		self.holmeslayer = nn.ModuleList([HolmesLayer(in_dim) for i in range(layer_num)])

	def forward(self, x, edge_index, batch):
		h = torch.zeros(1, x.shape[0], lstmHidden, device=x.device)
		c = torch.zeros(1, x.shape[0], lstmHidden, device=x.device)
		x_ = []
		for i, l in enumerate(self.holmeslayer):
			x, (h, c) = self.holmeslayer[i](x, edge_index, h, c)
			x_.append(torch.cat([gmp(x, batch), gap(x, batch)], dim=1))
		return x_[0]+x_[1]+x_[2]+x_[3]

class BCE(torch.nn.Module):   
	def __init__(self,in_dim):
		super(BCE,self).__init__()
		self.fc0 = nn.Linear(18,100)
		self.holmes = Holmes(in_dim)
		self.fc1 = nn.Linear(200,64)
		self.fc2 = nn.Linear(128,1)
		   
	def forward(self,x1,x2,e1,e2,y,batch1,batch2):
		x1 = self.fc0(x1)
		x2 = self.fc0(x2)
		op1 = F.leaky_relu(self.fc1(self.holmes(x1,e1,batch1)))
		op2 = F.leaky_relu(self.fc1(self.holmes(x2,e2,batch2)))
		op = torch.cat((op1,op2),1)
		op = self.fc2(op).squeeze()
		loss = loss_op(op,y)
		return (F.sigmoid(op)).detach().cpu().numpy(),loss