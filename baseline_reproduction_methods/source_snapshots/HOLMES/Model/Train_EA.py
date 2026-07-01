import time, itertools
import os, sys, os.path as osp
sys.path.append("/path/to/HOLMES/")
sys.path.append("/path/to/HOLMES/Model/")
import file_info_seperate
import holmesEA
import argparse, torch
import numpy as np
from torch_geometric.data import Dataset, Data, DataLoader
from sklearn.metrics import f1_score, precision_score, recall_score

def fetch_pairs(file, name):
	fd = open(file, 'r')
	contents = fd.read()
	pairs = contents.split('\n')
	pairs.remove(pairs[len(pairs)-1])
	dataset = []
	if name == "gcj":
		for pair in pairs:
			pair_arr = pair.split('\t')
			index = pair_arr[0].find('.java')
			pair_arr[0] = pair_arr[0][:index]
			pair_arr[0] = pair_arr[0].replace('gcjData', 'output')
			index = pair_arr[1].find('.java')
			pair_arr[1] = pair_arr[1][:index]
			pair_arr[1] = pair_arr[1].replace('gcjData', 'output')
			dataset.append(pair_arr)
		return dataset
	if name == "bcb":
		for pair in pairs:
			pair_arr = pair.split('\t')
			dataset.append(pair_arr)
		return dataset

class PairData(Data):
	def __inc__(self, key, value):
		if key == 'edgedata_index1' or key == 'edgecontrol_index1':
			return self.x1.size(0)
		if key == 'edgedata_index2' or key == 'edgecontrol_index2':
			return self.x2.size(0)
		else:
			return super(PairData, self).__inc__(key, value)
	def __cat_dim__(self, key, value):
		if 'index' in key or 'face' in key:
			return 1
		else:
			return 0

class GCJEAValDataset(Dataset):
	def __init__(self,root, transform=None, pre_transform=None):
		super(GCJEAValDataset, self).__init__(root, transform, pre_transform)

	@property
	def raw_file_names(self):
		return ["dev.txt"]
	@property
	def processed_file_names(self):
		return ['data_{}.pt'.format(i) for i in range(131726)]#288764

	def process(self):
		i = 0
		train_pairs = fetch_pairs(self.raw_paths[0])
		for pairs in train_pairs:
			print(i)
			matrix1_data, matrix1_control, encode1 = preprocess(pairs[0])
			matrix2_data, matrix2_control, encode2 = preprocess(pairs[1])
			if (pairs[2] == '-1'):
				labels = torch.Tensor([0])
			else:
				labels = torch.Tensor([1])
			data = PairData(x1=torch.Tensor(encode1), x2=torch.Tensor(encode2), edgedata_index1=torch.Tensor(matrix1_data), 
				edgedata_index2=torch.Tensor(matrix2_data), edgecontrol_index1=torch.Tensor(matrix1_control), 
				edgecontrol_index2=torch.Tensor(matrix2_control), y=labels)
			torch.save(data, osp.join(self.processed_dir, 'data_{}.pt'.format(i)))
			i += 1
	def len(self):
		return len(self.processed_file_names)
	def get(self, idx):
		data = torch.load(osp.join(self.processed_dir, 'data_{}.pt'.format(idx)))
		return data

class GCJEATrainDataset(Dataset):
	def __init__(self,root, transform=None, pre_transform=None):
		super(GCJEATrainDataset, self).__init__(root, transform, pre_transform)

	@property
	def raw_file_names(self):
		return ["train.txt"]
	@property
	def processed_file_names(self):
		return ['data_{}.pt'.format(i) for i in range(3000)]#288764

	def process(self):
		i = 0
		train_pairs = fetch_pairs(self.raw_paths[0])
		for pairs in train_pairs:
			print(i)
			matrix1_data, matrix1_control, encode1 = preprocess(pairs[0])
			matrix2_data, matrix2_control, encode2 = preprocess(pairs[1])
			if (pairs[2] == '-1'):
				labels = torch.Tensor([-1])
			else:
				labels = torch.Tensor([1])
			data = PairData(x1=torch.Tensor(encode1), x2=torch.Tensor(encode2), edgedata_index1=torch.Tensor(matrix1_data), 
				edgedata_index2=torch.Tensor(matrix2_data), edgecontrol_index1=torch.Tensor(matrix1_control), 
				edgecontrol_index2=torch.Tensor(matrix2_control), y=labels)
			torch.save(data, osp.join(self.processed_dir, 'data_{}.pt'.format(i)))
			i += 1
	def len(self):
		return len(self.processed_file_names)
	def get(self, idx):
		data = torch.load(osp.join(self.processed_dir, 'data_{}.pt'.format(idx)))
		return data

class GCJEATestDataset(Dataset):
	def __init__(self,root, transform=None, pre_transform=None):
		super(GCJEATestDataset, self).__init__(root, transform, pre_transform)

	@property
	def raw_file_names(self):
		return ["test.txt"]
		# return [""]
	@property
	def processed_file_names(self):
		return ['data_{}.pt'.format(i) for i in range(3000)]

	def process(self):
		i = 0
		train_pairs = fetch_pairs(self.raw_paths[0])
		for pairs in train_pairs:
			print(i)
			matrix1_data, matrix1_control, encode1 = preprocess(pairs[0])
			matrix2_data, matrix2_control, encode2 = preprocess(pairs[1])
			if (pairs[2] == '-1'):
				labels = torch.Tensor([-1])
			else:
				labels = torch.Tensor([1])
			data = PairData(x1=torch.Tensor(encode1), x2=torch.Tensor(encode2), edgedata_index1=torch.Tensor(matrix1_data), 
				edgedata_index2=torch.Tensor(matrix2_data), edgecontrol_index1=torch.Tensor(matrix1_control), 
				edgecontrol_index2=torch.Tensor(matrix2_control), y=labels)
			torch.save(data, osp.join(self.processed_dir, 'data_{}.pt'.format(i)))
			i += 1
	def len(self):
		return len(self.processed_file_names)
	def get(self, idx):
		data = torch.load(osp.join(self.processed_dir, 'data_{}.pt'.format(idx)))
		return data

class BCBEAValDataset(Dataset):
	def __init__(self,root, transform=None, pre_transform=None):
		super(BCBEAValDataset, self).__init__(root, transform, pre_transform)

	@property
	def raw_file_names(self):
		return ["dev.txt"]
	@property
	def processed_file_names(self):
		return ['data_{}.pt'.format(i) for i in range(3000)]

	def process(self):
		i = 0
		train_pairs = fetch_pairs(self.raw_paths[0])
		for pairs in train_pairs:
			print(i)
			matrix1_data, matrix1_control, encode1 = preprocess(pairs[0])
			matrix2_data, matrix2_control, encode2 = preprocess(pairs[1])
			if (pairs[2] == '-1'):
				labels = torch.Tensor([-1])
			else:
				labels = torch.Tensor([1])
			data = PairData(x1=torch.Tensor(encode1), x2=torch.Tensor(encode2), edgedata_index1=torch.Tensor(matrix1_data), 
				edgedata_index2=torch.Tensor(matrix2_data), edgecontrol_index1=torch.Tensor(matrix1_control), 
				edgecontrol_index2=torch.Tensor(matrix2_control), y=labels)
			torch.save(data, osp.join(self.processed_dir, 'data_{}.pt'.format(i)))
			i += 1
	def len(self):
		return len(self.processed_file_names)
	def get(self, idx):
		data = torch.load(osp.join(self.processed_dir, 'data_{}.pt'.format(idx)))
		return data

class BCBEATrainDataset(Dataset):
	def __init__(self,root,transform=None,pre_transform=None):
		super(BCBEATrainDataset, self).__init__(root, transform, pre_transform)

	@property
	def raw_file_names(self):
		return ["train.txt"]
	@property
	def processed_file_names(self):
		return ['data_{}.pt'.format(i) for i in range(3000)]#288764

	def process(self):
		i = 0
		train_pairs = fetch_pairs(self.raw_paths[0])
		for pairs in train_pairs:
			print(i)
			matrix1_data, matrix1_control, encode1 = preprocess(pairs[0])
			matrix2_data, matrix2_control, encode2 = preprocess(pairs[1])
			if (pairs[2] == '-1'):
				labels = torch.Tensor([-1])
			else:
				labels = torch.Tensor([1])
			data = PairData(x1=torch.Tensor(encode1), x2=torch.Tensor(encode2), edgedata_index1=torch.Tensor(matrix1_data), 
				edgedata_index2=torch.Tensor(matrix2_data), edgecontrol_index1=torch.Tensor(matrix1_control), 
				edgecontrol_index2=torch.Tensor(matrix2_control), y=labels)
			torch.save(data, osp.join(self.processed_dir, 'data_{}.pt'.format(i)))
			i += 1
	def len(self):
		return len(self.processed_file_names)
	def get(self, idx):
		data = torch.load(osp.join(self.processed_dir, 'data_{}.pt'.format(idx)))
		return data

class BCBEATestDataset(Dataset):
	def __init__(self,root, transform=None, pre_transform=None):
		super(BCBEATestDataset, self).__init__(root, transform, pre_transform)

	@property
	def raw_file_names(self):
		return ["test.txt"]
		# return [""]
	@property
	def processed_file_names(self):
		return ['data_{}.pt'.format(i) for i in range(3000)]

	def process(self):
		i = 0
		train_pairs = fetch_pairs(self.raw_paths[0])
		for pairs in train_pairs:
			print(i)
			matrix1_data, matrix1_control, encode1 = preprocess(pairs[0])
			matrix2_data, matrix2_control, encode2 = preprocess(pairs[1])
			if (pairs[2] == '-1'):
				labels = torch.Tensor([-1])
			else:
				labels = torch.Tensor([1])
			data = PairData(x1=torch.Tensor(encode1), x2=torch.Tensor(encode2), edgedata_index1=torch.Tensor(matrix1_data), 
				edgedata_index2=torch.Tensor(matrix2_data), edgecontrol_index1=torch.Tensor(matrix1_control), 
				edgecontrol_index2=torch.Tensor(matrix2_control), y=labels)
			torch.save(data, osp.join(self.processed_dir, 'data_{}.pt'.format(i)))
			i += 1
	def len(self):
		return len(self.processed_file_names)
	def get(self, idx):
		data = torch.load(osp.join(self.processed_dir, 'data_{}.pt'.format(idx)))
		return data

def train(name, num_epochs):
	if name == "gcj":
		dataset = GCJEATrainDataset(root="./gcjEA/train/")
		datasetval = GCJEAValDataset(root="./gcjEA/val/")
		datasettest = GCJEATestDataset(root="./gcjEA/test/")
		loader = DataLoader(dataset, batch_size=30, follow_batch=['x1', 'x2'], num_workers=24,shuffle=True)
		valloader = DataLoader(datasetval, batch_size=500, follow_batch=['x1', 'x2'], num_workers=24,shuffle=False)
		testloader = DataLoader(datasettest,batch_size=500, follow_batch=['x1','x2'], num_workers=24,shuffle=False)
	if name == "bcb":
		dataset = BCBEATrainDataset(root="./bcbEA/train/")
		datasetval = BCBEAValDataset(root="./bcbEA/val/")
		datasettest = BCBEATestDataset(root='./bcbEA/test/')
		loader = DataLoader(dataset, batch_size=30, follow_batch=['x1', 'x2'], num_workers=24,shuffle=True)
		valloader = DataLoader(datasetval, batch_size=500, follow_batch=['x1', 'x2'], num_workers=24,shuffle=False)
		testloader = DataLoader(datasettest, batch_size=500, follow_batch=['x1', 'x2'], num_workers=24,shuffle=False)
	
	for epoch in range(num_epochs):
		model.train()
		total_loss = 0
		print("Epoch: ",epoch)	
		counter = 0
		actual, predicted, predict_dev = [], [], []
		starttrain_time = time.time()
		for data in loader:
			counter += data.y.shape[0]
			x1 = data.x1.to(device)
			x1_batch = data.x1_batch.to(device)
			x2 = data.x2.to(device)
			x2_batch = data.x2_batch.to(device)
			eC1 = data.edgecontrol_index1.to(device)
			eD1 = data.edgedata_index1.to(device)
			eC2 = data.edgecontrol_index2.to(device)
			eD2 = data.edgedata_index2.to(device)
			y = data.y.to(device)
			y[y==-1] = 0
			optimizer.zero_grad()
			pred_,loss_ = model(x1,x2,eD1.long(),eC1.long(),eD2.long(),eC2.long(),y,x1_batch,x2_batch)
			(loss_).backward()
			optimizer.step()
			total_loss += loss_.item()*30
			if counter%900 == 0:
				print("Training Loss at Step",counter," is: ",total_loss/counter)
		endtrain_time = time.time()
		print("Total time for training",(endtrain_time-starttrain_time)/3600,"hrs \n Loss on training:",total_loss/526900)
	torch.save({'state_dict': model.state_dict(),'optimizer' : optimizer.state_dict()},name+"_holmes_EA_.pth")
	print("Model Saved")
	model.eval()
	for data in valloader:
		x1 = data.x1.to(device)
		x1_batch = data.x1_batch.to(device)
		x2 = data.x2.to(device)
		x2_batch = data.x2_batch.to(device)
		eC1 = data.edgecontrol_index1.to(device)
		eD1 = data.edgedata_index1.to(device)
		eC2 = data.edgecontrol_index2.to(device)
		eD2 = data.edgedata_index2.to(device)
		y = data.y.to(device)
		y[y==-1] = 0
		actual.append(y.tolist())
		with torch.no_grad():
			pred_,loss_ = model(x1,x2,eD1.long(),eC1.long(),eD2.long(),eC2.long(),y,x1_batch,x2_batch)
		predicted.append(pred_.tolist())
	predictions = list(itertools.chain.from_iterable(predicted))
	correct_dev = list(itertools.chain.from_iterable(actual))
	threshold = 0.2
	for i in range(6):
		predict_dev.append((np.array(predictions)>threshold)*1.0)
		threshold += 0.1
	maxstep = 0
	maxf1value = 0
	for i in range(6):
		f1score = f1_score(correct_dev, predict_dev[i])
		print(f1score)
		if f1score > maxf1value:
			maxf1value = f1score
			maxstep = i
	threshold = 0.2+maxstep*0.1
	print("decision threshold is: ",threshold,"\n F1 score on vaidation set: ",maxf1value)
	actual, predicted = [], []
	total_loss = counter = 0
	start_time = time.time()
	for data in testloader:
		counter += data.y.shape[0]
		x1 = data.x1.to(device)
		x1_batch = data.x1_batch.to(device)
		x2 = data.x2.to(device)
		x2_batch = data.x2_batch.to(device)
		eC1 = data.edgecontrol_index1.to(device)
		eD1 = data.edgedata_index1.to(device)
		eC2 = data.edgecontrol_index2.to(device)
		eD2 = data.edgedata_index2.to(device)
		y = data.y.to(device)
		y[y==-1] = 0
		actual.append(y.tolist())
		with torch.no_grad():
			pred_,loss_ = model(x1,x2,eD1.long(),eC1.long(),eD2.long(),eC2.long(),y,x1_batch,x2_batch)
		predicted.append((pred_>threshold).tolist())
		total_loss += loss_.item()*500
		if counter%1000 == 0:
			print("Test Loss at Step",counter," is: ",total_loss/counter)
	predicted = list(itertools.chain.from_iterable(predicted))
	actual = list(itertools.chain.from_iterable(actual))
	end_time = time.time()
	print("Total time taken for evaluation is: ",(end_time - start_time)/3600,"hrs.") 
	print("Loss on test set:",total_loss/282271,"\n F1 Score: ",f1_score(actual,predicted),"\n precision score: ",precision_score(actual, predicted),"\n recall score: ",recall_score(actual,predicted))

	

my_parser = argparse.ArgumentParser(description='List the dataset(gcj|bcb), and the number of training epochs (N)')
my_parser.add_argument('name',metavar='name',type=str,help='the name of the dataset')
my_parser.add_argument('N',metavar='n',type=int,help='# of training+_epochs')
args = my_parser.parse_args()
name = args.name
num_epochs = args.N
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


model = holmesEA.BCE(100).to(device)
optimizer = torch.optim.Adam(model.parameters(),lr=0.0002, weight_decay=0)
print(model,optimizer)
torch.nn.DataParallel(model)
train(name,num_epochs)

