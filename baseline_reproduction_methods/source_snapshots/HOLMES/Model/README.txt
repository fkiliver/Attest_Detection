Modelling Functional Similarity in Source Code through Graph-Based Siamese Neural Networks
-----------------------------------------------------------------------------------------------

This Repository contains the scripts required to train and evaluate HOLMES variants on GCJ and BCB dataset. 

"GCJ" folder contains compressed data for google code jam dataset for HOLMES-EA and HOLMES-EU variants with folder names gcjEA and gcjEU respectively. 
"BCB" folder contains compressed data for big clone bench dataset for HOLMES-EA and HOLMES-EU variants with folder names bcbEA and bcbEU respectively. 

Folder "Model" contains the architecture for HOLMES-EA and HOLMES-EU variant.

file_info_seperate.py and file_info.py generates node feature matrix and graph adjacency list for the PDGs of GCJ and BCB dataset.

To run HOLMES-EA variant on GCJ or BCB dataset run the script Train_EA.py with the following command:
	python Train_EA.py dataset_name(gcj|bcb) number_of_training_epochs

To run HOLMES-EU variant on GCJ or BCB dataset run the script Train_EU.py with the following command:
	python Train_EU.py dataset_name(gcj|bcb) number_of_training_epochs

In our experiments we have trained HOLMES-EA and HOLMES-EU for 14 epochs for google code jam and for BCB 5 epochs for HOLMES-EA and 10 epochs for HOLMES-EU variant. 
We have used Adam optimizer with learning rate set to 0.0002. We have reduced the learning rate to 0.00002 at 10th epoch for GCJ dataset.
We have used GTx 2080Ti GPU to run our experiments. Each epoch has taken around 2.5 hours to complete on our server configuration.