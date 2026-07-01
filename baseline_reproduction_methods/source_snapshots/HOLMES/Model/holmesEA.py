import time, itertools,os,pickle
import numpy as np
import torch,torchvision
from torch_geometric.nn import GATConv,SAGPooling,GCNConv,JumpingKnowledge, GlobalAttention
import torch.nn.functional as F, torch.nn as nn
from torch_geometric.nn import global_mean_pool as gap, global_max_pool as gmp, global_add_pool as gaddp

layer_num = 4
inDim = lstmHidden = 100
loss_op = nn.BCEWithLogitsLoss()

class Breadth(torch.nn.Module):
	def __init__(self, in_dim, out_dim):
		super(Breadth, self).__init__()
		self.conv1 = GATConv(in_dim, out_dim, heads = 8)
		self.lin1 = nn.Linear(in_dim,out_dim*8)
		self.conv3 = GATConv(8*in_dim, out_dim, heads=6, concat=False)
		self.lin3 = torch.nn.Linear(8*in_dim, out_dim)

	def forward(self, x, edge_index):
		x = F.leaky_relu(self.conv1(x, edge_index) + self.lin1(x),inplace=False)
		x = F.leaky_relu(self.conv3(x, edge_index) + self.lin3(x),inplace=False)
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
		self.breadthD_func = Breadth(in_dim, in_dim)
		self.breadthC_func = Breadth(in_dim, in_dim)
		self.depthD_func = Depth(in_dim, lstmHidden)
		self.depthC_func = Depth(in_dim, lstmHidden)

	def forward(self, xD, xC, edgedata_index,edgecontrol_index,hD,cD,hC,cC):
		xD = self.breadthD_func(xD, edgedata_index)
		xD = xD[None, :]
		xD, (hD,cD) = self.depthD_func(xD,hD,cD)
		xD = xD[0]
		xC = self.breadthC_func(xC, edgecontrol_index)
		xC = xC[None, :]
		xC, (hC,cC) = self.depthC_func(xC,hC,cC)
		xC = xC[0]
		return xD, (hD,cD), xC, (hC,cC)

class Holmes(torch.nn.Module):
	def __init__(self, in_dim):
		super(Holmes, self).__init__()
		self.holmeslayer = nn.ModuleList([HolmesLayer(in_dim) for i in range(layer_num)])
		self.gateC = nn.Linear(500,1)	
		self.nnC = nn.Linear(500,200)
		self.gatennC = GlobalAttention(self.gateC,self.nnC)
		self.gateD = nn.Linear(500,1)   
		self.nnD = nn.Linear(500,200)
		self.gatennD = GlobalAttention(self.gateD,self.nnD)
		self.jk = JumpingKnowledge("cat")


	def forward(self, x, edgedata_index,edgecontrol_index, batch):
		hC = torch.zeros(1, x.shape[0], lstmHidden, device=x.device)
		cC = torch.zeros(1, x.shape[0], lstmHidden, device=x.device)
		hD = torch.zeros(1, x.shape[0], lstmHidden, device=x.device)
		cD = torch.zeros(1, x.shape[0], lstmHidden, device=x.device)
		xD_, xC_ = [x], [x]
		xD = xC = x
		residual = x
		for i, l in enumerate(self.holmeslayer):
			xD,(hD,cD),xC,(hC,cC) = self.holmeslayer[i](xD,xC,edgedata_index,edgecontrol_index,hD,cD,hC,cC)
			xD_ += [xD]
			xC_ += [xC]
			xD = residual + xD
			xC = residual + xC
		xD = self.gatennD(self.jk(xD_),batch)
		xC = self.gatennC(self.jk(xC_),batch)
		x = xD + xC
		return x


class BCE(torch.nn.Module):   
	def __init__(self,in_dim):
		super(BCE,self).__init__()
		self.fc0 = nn.Linear(18,100)
		self.holmes = Holmes(in_dim)
		self.fc3 = nn.Linear(400,128)
		self.fc2 = nn.Linear(128,1)
		   
	def forward(self,x1,x2,eD1,eC1,eD2,eC2,y,batch1,batch2):
		x1 = self.fc0(x1)
		x2 = self.fc0(x2)
		op1 = self.holmes(x1,eD1,eC1,batch1)
		op2 = self.holmes(x2,eD2,eC2,batch2)
		op = torch.cat((op1,op2),dim=1)
		op = F.leaky_relu(self.fc3(op))
		op = self.fc2(op)
		loss = loss_op(op.view(-1,1),y.view(-1,1))
		return (F.sigmoid(op)).detach().cpu().numpy(),loss


