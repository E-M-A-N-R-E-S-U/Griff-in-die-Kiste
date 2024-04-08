import os

import numpy.exceptions
import torch
import torch.nn as nn
from torch.utils.data import Dataset, random_split
import pandas as pd
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix, f1_score
from P020_Backend.P021_Code.CloudProcessing import Cloud


class PointCloudSet(Dataset):

    def __init__(self, results_file, feature_path, train: bool = True):
        super().__init__()

        results_df = pd.read_csv(results_file, sep=";")
        self.path_to_feature_files = feature_path
        if train:
            self.feature_files = results_df.loc[results_df["use_case"] == "train"].iloc[:, 0].to_numpy()
            self.label = results_df.loc[results_df["use_case"] == "train"].iloc[:, 2:10].to_numpy()
        else:
            self.feature_files = results_df.loc[results_df["use_case"] == "test"].iloc[:, 0].to_numpy()
            self.label = results_df.loc[results_df["use_case"] == "test"].iloc[:, 2:10].to_numpy()

        self.features = []
        for feature_file in self.feature_files:
            self.features.append(self.get_features(feature_file))
        self.equalize_shapes()

    def equalize_shapes(self):
        max_shape = (0, 0)
        for ind, feature in enumerate(self.features):
            if feature.shape[0] > feature.shape[1]:
                self.features[ind] = np.rot90(feature)
            if self.features[ind].shape > max_shape:
                max_shape = self.features[ind].shape

        for ind, feature in enumerate(self.features):
            if feature.shape < max_shape:
                self.features[ind] = np.pad(feature, ((0, max_shape[0] - feature.shape[0]),
                                                      (0, max_shape[1] - feature.shape[1])))

        self.features = np.asarray(self.features)

    def get_features(self, feature_file):
        cloud = Cloud()
        filepath = os.path.join(self.path_to_feature_files, feature_file)
        cloud.set(filepath)
        df = cloud.get_heatmap(voxel_size=10)
        features_np = df.to_numpy()
        # Min-Max standardization
        features_np = (features_np - np.min(features_np)) / (np.max(features_np) - np.min(features_np))

        return features_np

    def __len__(self):
        return len(self.label)

    def __getitem__(self, idx):
        features = self.features[idx]
        label = self.label[idx]

        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"

        features = torch.from_numpy(features).float().to(device)
        label = torch.from_numpy(label).float().to(device)

        return features, label


class Network(nn.Module):

    def __init__(self, model_size, lr=0.001, all_labels: list = None, model=None):
        super().__init__()
        # self.max_pool = nn.MaxPool2d(2, (2, 2))
        # self.avg_pool = nn.AvgPool2d(2, (2, 2))

        self.flatten = nn.Flatten()
        self.model = self.get_model(model_size)
        if model:
            self.model.load_state_dict(torch.load(model))
        self.device = "cpu"
        if torch.cuda.is_available():
            self.device = "cuda"
        self.model.to(self.device)
        # Pass the optimizer the parameters to optimize
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.CrossEntropyLoss()

        if all_labels:
            self.all_labels = all_labels
        else:
            self.all_labels = np.array(["lo", "o", "ro", "l", "r", "lu", "u", "ru"])

    @staticmethod
    def get_model(model_size):
        models = {"3x3": nn.Sequential(nn.Linear(400, 600),
                                       nn.ReLU(),
                                       nn.BatchNorm1d(600),
                                       nn.Linear(600, 300),
                                       nn.ReLU(),
                                       nn.BatchNorm1d(300),
                                       nn.Linear(300, 8)),
                  "5x5": nn.Sequential(nn.Linear(1066, 500),
                                       nn.ReLU(),
                                       nn.BatchNorm1d(500),
                                       nn.Linear(500, 250),
                                       nn.ReLU(),
                                       nn.BatchNorm1d(250),
                                       nn.Linear(250, 50),
                                       nn.ReLU(),
                                       nn.BatchNorm1d(50),
                                       nn.Linear(50, 8))
                  }

        return models[model_size]

    def forward(self, x):
        x = self.flatten(x)
        return self.model(x)

    def perform_training(self, train_loader, valid_loader, frame=None, epochs=500, memory_path=os.getcwd()):
        loss_history = []
        train_predictions = np.array([])
        train_labels = np.array([])

        valid_predictions = np.array([])
        valid_labels = np.array([])

        frame.results.clear_all()
        frame.options.disable_start_training()
        frame.results.set_status("Training gestartet")

        for t in range(epochs):
            message = f"\nEpoche {t + 1}\n---------------------------------------------------------"
            frame.results.update_console(message)

            # Perform training
            self.model.train()
            for batch_nb, (X, y), in enumerate(train_loader):
                # get true label
                det_y = y.cpu().detach().numpy().squeeze()
                try:
                    true_idx = det_y.argmax(1)
                except numpy.exceptions.AxisError:
                    true_idx = det_y.argmax()
                train_labels = np.append(train_labels, self.all_labels[true_idx])

                # compute prediction
                y_pred = self(X)
                det_y_pred = y_pred.cpu().detach().numpy().squeeze()
                try:
                    pred_idx = det_y_pred.argmax(1)
                except numpy.exceptions.AxisError:
                    pred_idx = det_y_pred.argmax()
                train_predictions = np.append(train_predictions, self.all_labels[pred_idx])

                # compute loss
                loss = self.loss_fn(y_pred, y)

                # reset gradients before iteration
                self.optimizer.zero_grad()
                # performe backward step (calculate gradients)
                loss.backward()
                # update model weights with gradients
                self.optimizer.step()

                loss, passed_batches = loss.item(), batch_nb * len(X)
                if passed_batches % 10 == 0:
                    message = f"loss: {loss:>7f}, passed batches: [{passed_batches:>5d}/{len(train_loader.dataset):>5d}]"
                    frame.results.update_console(message)
                    frame.results.update_progress(t/epochs*100)
                    loss_history.append(loss)

                if t % 10 == 0:
                    file_path = os.path.join(memory_path, f"GraspDirection_Model_Epoch_{t}.pth")
                    torch.save(self.model.state_dict(), file_path)

            # Perform validation
            self.model.eval()
            for batch_nb, (X, y), in enumerate(valid_loader):
                # Get true labels
                det_y = y.cpu().detach().numpy().squeeze()
                try:
                    true_idx = np.argmax(det_y, axis=1)
                except np.exceptions.AxisError:
                    true_idx = np.argmax(det_y)
                valid_labels = np.append(valid_labels, self.all_labels[true_idx])

                # Get prediction
                y_pred = self(X)
                det_y_pred = y_pred.cpu().detach().numpy().squeeze()
                try:
                    pred_idx = np.argmax(det_y_pred, axis=1)
                except np.exceptions.AxisError:
                    pred_idx = np.argmax(det_y_pred)
                valid_predictions = np.append(valid_predictions, self.all_labels[pred_idx])

            train_accuracy = accuracy_score(train_labels, train_predictions)
            valid_accuracy = accuracy_score(valid_labels, valid_predictions)
            frame.results.update_training_history(loss_history, train_accuracy, valid_accuracy)

            if frame.options.stop.get():
                frame.options.enable_start_training()
                frame.results.set_status("Training beendet")
                break

        frame.options.enable_start_training()
        frame.results.set_status("Training beendet")

    def hardmax(self, array):
        max_ind = np.argmax(array)
        hardmax = np.zeros_like(array)
        hardmax[max_ind] = 1
        return hardmax

    def perform_test(self, dataloader, frame=None):
        frame.options.disable_start_test()
        frame.results.clear_all()
        frame.results.set_status("Test gestartet")

        self.model.eval()

        predictions = np.array([])
        labels = np.array([])
        for batch_nb, (X, y) in enumerate(dataloader):
            # Labels
            det_y = y.cpu().detach().numpy().squeeze()
            try:
                true_idx = np.argmax(det_y, axis=1)
            except np.exceptions.AxisError:
                true_idx = np.argmax(det_y)
            labels = np.append(labels, self.all_labels[true_idx])
            # Predictions
            y_pred = self(X)
            det_y_pred = y_pred.cpu().detach().numpy().squeeze()
            try:
                pred_idx = np.argmax(det_y_pred, axis=1)
            except np.exceptions.AxisError:
                pred_idx = np.argmax(det_y_pred)
            predictions = np.append(predictions, self.all_labels[pred_idx])
            accuracy = accuracy_score(labels, predictions)
            # precision = precision_score(labels, predictions, average="macro")
            f1 = f1_score(labels, predictions, labels=self.all_labels, average="macro", zero_division=0.0)
            conf_matrix = confusion_matrix(list(labels), list(predictions), labels=self.all_labels)
            df_cm = pd.DataFrame(conf_matrix, self.all_labels, self.all_labels)
            frame.results.update_progress(batch_nb / len(dataloader) * 100)
            frame.results.update_test_history(batch_nb, f1, accuracy, df_cm)

            if frame.options.stop.get():
                frame.options.enable_start_test()
                frame.results.set_status("Test beendet")
                break

        frame.options.enable_start_test()
        frame.results.reset_progress()
        frame.results.set_status("Test beendet")
