import seaborn as sn
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
plt.rcParams.update({'font.size': 8})


class TrainingResPlot:
    """
    A class that defines training result plots

    ...

    Attributes
    ----------
    fig : Any
        The matplotlib figure
    ax : Any
        The axis object of the figure

    Methods
    -------
    clear()
        Resets the plots to its default values
    get()
        Returns the figure
    update(train_accuracy, valid_accuracy, loss)
        Updates the plot data with the transferred data

    """

    def __init__(self):
        self.fig, self.ax = plt.subplots(2, 1, constrained_layout=True)
        # self.fig.suptitle("Training History", fontsize=12)
        self.ax[0].set_xticks([])
        self.ax[0].set_title("Loss History")
        self.ax[0].set_ylim((0, 1))
        self.ax[0].set_ylabel("Loss", fontsize=8)
        self.ax[1].set_xlim((0, 100))
        self.ax[1].set_ylim((0, 1))
        self.ax[1].set_title("Accuracy")
        self.ax[1].set_xlabel("Iterations", fontsize=8)
        self.ax[1].set_ylabel("Accuracy", fontsize=8)

    def clear(self):
        """
        Resets the plots to its default values

        """
        self.ax[0].clear()
        self.ax[0].set_xticks([])
        self.ax[0].set_title("Loss History")
        self.ax[0].set_ylabel("Loss", fontsize=8)
        self.ax[1].clear()
        self.ax[1].set_title("Accuracy")
        self.ax[1].set_xlabel("Iterations", fontsize=8)
        self.ax[1].set_ylabel("Accuracy", fontsize=8)

    def get(self):
        """
        Returns the figure

        """
        return self.fig

    def update(self, train_accuracy, valid_accuracy, loss):
        """
        Updates the plot data with the transferred data

        Parameter
        --------
        train_accuracy : Any
            The accuracy computed on the training data
        valid_accuracy : Any
            The accuracy computed on the validation data
        loss : Any
            The loss over the epochs passed through

        """
        l = np.array(loss)
        ta = np.array(train_accuracy)
        va = np.array(valid_accuracy)

        self.clear()
        self.ax[0].plot(l, color='r', label="training")
        self.ax[0].legend()
        self.ax[1].plot(ta, color='r', label="training")
        self.ax[1].plot(va, color='g', label="validation")
        self.ax[1].legend()


class TestResPlot:
    """
    A class that defines test result plots

    ...

    Attributes
    ----------
    fig : Any
        The matplotlib figure
    ax_dict : Any
        A dictionary that contains the axis objects of the figure


    Methods
    -------
    get()
        Returns the figure
    clear()
        Resets the plots to its default values
    update(conf_mat, accuracy, f1, epochs)
        Updates the plot data with the transferred data

    """

    def __init__(self):
        self.fig = plt.Figure(layout="constrained")
        grid_kws = {'width_ratios': (1, 0.05, 1), 'wspace': 0.05}
        self.ax_dict = self.fig.subplot_mosaic([["conf", "cbar", "f1"],
                                                ["conf", "cbar", "acc"]],
                                               gridspec_kw=grid_kws)
        all_labels = ["lo", "o", "ro", "l", "r", "lu", "u", "ru"]
        init_df_cm = pd.DataFrame(np.identity(8), all_labels, all_labels)
        sn.heatmap(init_df_cm, annot=True, cmap="rocket_r", ax=self.ax_dict["conf"], cbar_ax=self.ax_dict["cbar"])
        self.ax_dict["conf"].set_ylim(0, 8)
        self.ax_dict["conf"].set_xlabel("Predicted")
        self.ax_dict["conf"].set_ylabel("Actual")
        self.ax_dict["conf"].invert_yaxis()

        self.ax_dict["f1"].set_title("F1-Score")
        self.ax_dict["f1"].set_xticks([])
        self.ax_dict["f1"].set_ylim((0, 1))
        self.ax_dict["f1"].set_ylabel("F1-Score", fontsize=8)
        self.ax_dict["acc"].set_xlim((0, 100))
        self.ax_dict["acc"].set_ylim((0, 1))
        self.ax_dict["acc"].set_title("Accuracy")
        self.ax_dict["acc"].set_xlabel("Iterations", fontsize=8)
        self.ax_dict["acc"].set_ylabel("Accuracy", fontsize=8)

    def get(self):
        """
        Returns the figure

        """
        return self.fig

    def clear(self):
        """
        Resets the plots to its default values

        """
        self.ax_dict["f1"].clear()
        self.ax_dict["f1"].set_title("F1-Score")
        self.ax_dict["f1"].set_xticks([])
        self.ax_dict["f1"].set_ylabel("F1-Score", fontsize=8)
        self.ax_dict["acc"].clear()

        self.ax_dict["acc"].set_title("Accuracy")
        self.ax_dict["acc"].set_xlabel("Iterations", fontsize=8)
        self.ax_dict["acc"].set_ylabel("Accuracy", fontsize=8)

    def update(self, conf_mat, accuracy, f1, epochs):
        """
        Updates the plot data with the transferred data

        Parameter
        ---------
        conf_mat : Any
            The confusion matrix computed on the test data
        accuracy : Any
            The accuracy computed on the test data
        f1 : Any
            The f1-score computed on the test data
        epochs : Any
            The epochs passed

        """
        x = np.array(epochs)
        f = np.array(f1)
        a = np.array(accuracy)

        self.ax_dict["f1"].plot(x, f, color='r')
        self.ax_dict["acc"].plot(x, a, color='r')

        self.ax_dict["conf"].clear()
        # vmin=0, vmax=100,
        sn.heatmap(conf_mat, annot=True, cmap="rocket_r", ax=self.ax_dict["conf"],
                   cbar_ax=self.ax_dict["cbar"])
        self.ax_dict["conf"].set_ylim(0, 8)
        self.ax_dict["conf"].set_xlabel("Predicted")
        self.ax_dict["conf"].set_ylabel("Actual")
        self.ax_dict["conf"].invert_yaxis()
