# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 21:38:07 2018

@author: Ariel Domingo Catli
"""

import numpy as np
import cv2
import pickle
import os
from sklearn.svm import SVC
import shutil


class Classifier:
    
    def __init__(self, isHOG):
        self.dataset_X = []
        self.dataset_Y = []
        self.dataset = []
        self.__model = []
        self.dataset_X_test = []
        self.dataset_Y_test = []
        self.dataset_filenames_test = []
        self.dataset_filenames_nodir_test = []
        self.dataset_test = []
        self.isHOG = isHOG
        
    def add_model_dataset(self, data_folder, data_class):
        if os.path.exists(data_folder):
            images = os.listdir(data_folder)
            
            if self.isHOG:
                HOG = cv2.HOGDescriptor()
                for image in images:
                    file_name = data_folder + image
                    image = cv2.imread(file_name)
                    image_hog = HOG.compute(image)
                    self.dataset_X.append(image_hog)
                    self.dataset_Y.append(data_class)
                    
            elif self.isHOG == False:
                
                for image in images:
                    img_hist = np.zeros([])
                    file_name = data_folder + image
                    image = cv2.imread(file_name)
                    mask_image = cv2.threshold(cv2.GaussianBlur(cv2.imread(file_name, 0), (7,7), 0),127,255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
                    r = cv2.calcHist([image], [0], mask_image[1], [256], [0,256])
                    r = r/max(r)
                    g = cv2.calcHist([image], [1], mask_image[1], [256], [0,256])
                    g = g/max(g)
                    b = cv2.calcHist([image], [2], mask_image[1], [256], [0,256])
                    b = b/max(b)
                   
                    img_hist = np.concatenate((r,g,b))
                    
                    self.dataset_X.append(img_hist)
                    self.dataset_Y.append(data_class)
            
    
    def build_model_dataset(self, model_dataset_folder, model_dataset_name):
        
        if self.isHOG:
            self.dataset_X = np.array(self.dataset_X).reshape(-1,3780)
            self.dataset_Y = np.array(self.dataset_Y)
        else:
            self.dataset_X = np.array(self.dataset_X).reshape(-1, 768)
            self.dataset_Y = np.array(self.dataset_Y)
            
        self.dataset = [self.dataset_X, self.dataset_Y]
        with open(model_dataset_folder+model_dataset_name+".bin", "wb") as dataset:
            pickle.dump(self.dataset, dataset)
            
    def add_test_dataset(self, data_folder, data_class):
        if os.path.exists(data_folder):
            images = os.listdir(data_folder)
            
            if self.isHOG:
                HOG = cv2.HOGDescriptor()
                for image in images:
                    file_name = data_folder + image
                    image_ = cv2.imread(file_name)
                    image_hog = HOG.compute(image_)
                    self.dataset_X_test.append(image_hog)
                    self.dataset_Y_test.append(data_class)
                    self.dataset_filenames_nodir_test.append(image)
                    self.dataset_filenames_test.append(file_name)
                    
            elif self.isHOG == False:
                
                for image in images:
                    img_hist = np.zeros([])
                    file_name = data_folder + image
                    image_ = cv2.imread(file_name)
                    mask_image = cv2.threshold(cv2.GaussianBlur(cv2.imread(file_name, 0), (7,7), 0),127,255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
                    r = cv2.calcHist([image_], [0], mask_image[1], [256], [0,256])
                    r = r/max(r)
                    g = cv2.calcHist([image_], [1], mask_image[1], [256], [0,256])
                    g = g/max(g)
                    b = cv2.calcHist([image_], [2], mask_image[1], [256], [0,256])
                    b = b/max(b)
                   
                    img_hist = np.concatenate((r,g,b))
                    
                    self.dataset_X_test.append(img_hist)
                    self.dataset_Y_test.append(data_class)
                    self.dataset_filenames_nodir_test.append(image)
                    self.dataset_filenames_test.append(file_name)
                    
    
    def build_test_dataset(self, test_dataset_folder, test_dataset_name):
        if self.isHOG:
            self.dataset_X_test = np.array(self.dataset_X_test).reshape(-1,3780)
            self.dataset_Y_test = np.array(self.dataset_Y_test)
        else:
            self.dataset_X_test = np.array(self.dataset_X_test).reshape(-1, 768)
            self.dataset_Y_test = np.array(self.dataset_Y_test)
            
        self.dataset_test = [self.dataset_X_test, self.dataset_Y_test, self.dataset_filenames_test, self.dataset_filenames_nodir_test]
        with open(test_dataset_folder+test_dataset_name+".bin", "wb") as dataset:
            pickle.dump(self.dataset_test, dataset)
            
    def build_model(self, model_folder, model_name):
        
        self.__model = SVC(gamma = 0.0001, C=100)
        if(len(self.dataset) != 0):
            self.__model.fit(self.dataset_X, self.dataset_Y)
        
        with open(model_folder+model_name+".bin", "wb") as model:
            pickle.dump(self.__model, model)
            
    def load_model(self, model_folder):
        with open(model_folder, "rb") as dataset:
            return pickle.load(dataset)  
        
            
    def load_dataset(self, dataset_folder):
        with open(dataset_folder, "rb") as dataset:
            return pickle.load(dataset)
    
    #def test(class1_dest, class0_dest, dataset=self.dataset_test, model=self.__model):
        
    def classify(self, class0_dest, class1_dest):
        count = 0
        correct = 0
        
        TP = 0
        TN = 0
        FP = 0
        FN = 0
        
        results = self.__model.predict(self.dataset_test[0])
        count = len(results)
        for i, result in enumerate(results):
            if result == 1:
                shutil.copy(str(self.dataset_filenames_test[i]), str(class1_dest)+str(self.dataset_filenames_nodir_test[i]))
            else:
                shutil.copy(str(self.dataset_filenames_test[i]), str(class0_dest)+str(self.dataset_filenames_nodir_test[i]))
                
            if result == self.dataset_Y_test[i]:
                correct += 1
            
            if result == 1 and result == self.dataset_Y_test[i]:
                TP += 1
            
            if result == 0 and result == self.dataset_Y_test[i]:
                TN += 1
                
            if result == 0 and self.dataset_Y_test[i] == 1:
                FN += 1
            
            if result == 1 and self.dataset_Y_test[i] == 0:
                FP += 1
        
        return [results, self.dataset_filenames_test, [correct, count], [TP, TN, FP, FN]]
                
    
    #def add_test_dataset(self): 
        
if __name__ == "__main__":
    bkn = Classifier(True)
    bkn.add_model_dataset("../../training/bkn/data/bkn/", 0)
    bkn.add_model_dataset("../../training/bkn/data/unbkn/", 1)
    bkn.build_model_dataset("../../training/bkn/bins/", "bkn_dataset")
    bkn.build_model("../../training/bkn/bins/", "model_bkn")
    bkn.add_test_dataset("../../testing/bkn/data/bkn/", 0)
    bkn.add_test_dataset("../../testing/bkn/data/unbkn/", 1)
    bkn.build_test_dataset("../../testing/bkn/bins/", "bkn_test_dataset")
    results = bkn.classify("../../testing/bkn/results/bkn/", "../../testing/bkn/results/unbkn/")
    print(results[2][0]/results[2][1])
    print(results[3])
    
    ylw = Classifier(False)
    ylw.add_model_dataset("../../training/ylw/data/ylw/", 1)
    ylw.add_model_dataset("../../training/ylw/data/nylw/", 0)
    ylw.build_model_dataset("../../training/ylw/bins/", "ylw_dataset")
    ylw.build_model("../../training/ylw/bins/", "model_ylw")
    ylw.add_test_dataset("../../testing/ylw/data/ylw/", 1)
    ylw.add_test_dataset("../../testing/ylw/data/nylw/", 0)
    ylw.build_test_dataset("../../testing/ylw/bins/", "ylw_test_dataset")
    results = ylw.classify("../../testing/ylw/results/ylw/", "../../testing/ylw/results/nylw/")
    print(results[2][0]/results[2][1])
    print(results[3])
    
    grn = Classifier(False)
    grn.add_model_dataset("../../training/grn/data/grn/", 1)
    grn.add_model_dataset("../../training/grn/data/ngrn/", 0)
    grn.build_model_dataset("../../training/grn/bins/", "grn_dataset")
    grn.build_model("../../training/grn/bins/", "model_grn")
    grn.add_test_dataset("../../testing/grn/data/grn/", 1)
    grn.add_test_dataset("../../testing/grn/data/ngrn/", 0)
    grn.build_test_dataset("../../testing/grn/bins/", "grn_test_dataset")
    results = grn.classify("../../testing/grn/results/grn/", "../../testing/grn/results/ngrn/")
    print(results[2][0]/results[2][1])
    print(results[3])
#   
    paddy = Classifier(False)
    paddy.add_model_dataset("../../training/paddy/data/paddy/", 1)
    paddy.add_model_dataset("../../training/paddy/data/npaddy/", 0)
    paddy.build_model_dataset("../../training/paddy/bins/", "paddy_dataset")
    paddy.build_model("../../training/paddy/bins/", "model_paddy")
    paddy.add_test_dataset("../../testing/paddy/data/paddy/", 1)
    paddy.add_test_dataset("../../testing/paddy/data/npaddy/", 0)
    paddy.build_test_dataset("../../testing/paddy/bins/", "paddy_test_dataset")
    results = paddy.classify("../../testing/paddy/results/paddy/", "../../testing/paddy/results/npaddy/")
    print(results[2][0]/results[2][1])
    print(results[3])
    
    