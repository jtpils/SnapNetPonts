import numpy as np
import os
# from plyfile import PlyData, PlyElement
import scipy.misc
import pickle
from tqdm import *
import tensorflow as tf
import shutil
import json
#limit to only one GPU
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="2"

from python.tensorflow_tester_backprojeter import BackProjeter
import python.models.tensorflow_unet as model
import python.models.tensorflow_residual_fusion as model_fusion

print("Loading configuration file")
# Training settings
import argparse
parser = argparse.ArgumentParser(description='Semantic3D')
parser.add_argument('--config', type=str, default="config_scannet.json", metavar='N',
help='config file')
args = parser.parse_args()
json_data=open(args.config).read()
config = json.loads(json_data)

filenames = ["scene_test_" + str(j) for j in range(312)]


imsize = config["imsize"]
directory = config["test_results_root_dir"]
voxels_directory = os.path.join(directory,"voxels")
dir_images = os.path.join(directory,config["images_dir"])
saver_directory_rgb = config["saver_directory_rgb"]
saver_directory_composite = config["saver_directory_composite"]
saver_directory_fusion = config["saver_directory_fusion"]

label_nbr = config["label_nbr"]
batch_size = config["batch_size"]
input_ch = config["input_ch"]


save_dir = config["output_directory"]

if not os.path.exists(save_dir):
    os.makedirs(save_dir)


backproj = BackProjeter(model.model, model.model, model_fusion.model)

for filename in filenames:

    backproj.backProj(
        filename=filename,
        label_nbr=label_nbr,
        dir_data=voxels_directory,
        dir_images=dir_images,
        imsize=imsize,
        input_ch=input_ch,
        batch_size=batch_size,
        saver_directory1=saver_directory_rgb,
        saver_directory2=saver_directory_composite,
        saver_directoryFusion=saver_directory_fusion,
        images_root1="rgb",
        images_root2="composite",
        variable_scope1="rgb",
        variable_scope2="composite",
        variable_scope_fusion="fusion")

    backproj.saveScores(os.path.join(save_dir, filename+"_scores"))
    backproj.createLabelPLY(filename, dir_data=voxels_directory, save_dir=save_dir)
