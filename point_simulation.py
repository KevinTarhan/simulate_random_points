import numpy as np
from qtpy import QtWidgets
import flika
flika_version = flika.__version__
from flika import global_vars as g
from flika.process.BaseProcess import BaseProcess_noPriorWindow, SliderLabel
from flika.process.file_ import save_file_gui
from qtpy.QtWidgets import *
from qtpy.QtCore import *
import os.path
import matplotlib.pyplot as plt
from .neighbor_dist import distances
from flika.logger import logger


def save_text_file(text, filename=None):
    """save_text_file(text, filename=None)
        Save a string to a text file

        Parameters:
            filename (str): Text will be saved here
            text (str): Text to be saved

        Returns:
            Tuple with directory filename is stored in and filename's location

        """
    if filename is None or filename is False:
        filetypes = '*.txt'
        prompt = 'Save File As Txt'
        filename = save_file_gui(prompt, filetypes=filetypes)
        if filename is None:
            return None
    g.m.statusBar().showMessage('Saving Points in {}'.format(os.path.basename(filename)))
    file = open(filename, 'w')
    file.write(text)
    file.close()
    g.m.statusBar().showMessage('Successfully saved {}'.format(os.path.basename(filename)))
    directory = os.path.dirname(filename)
    return directory, filename


def compute_neighbor_distance(base_directory, file_directory):
    save_box = QWidget()
    full_dir = r'{file}'.format(file=file_directory)
    file_output, ok = QInputDialog.getText(save_box, "Neighbor Distance", """Output filename?""")
    if not ok:
        return
    output_dir = r'{dir}/{file}.txt'.format(dir=base_directory, file=file_output)
    logger.debug(full_dir)
    distances(full_dir, full_dir, output_dir)


class PointSim(BaseProcess_noPriorWindow):

    def __init__(self):
        super().__init__()
        self.__name__ = self.__class__.__name__

    def get_init_settings_dict(self):
        s = dict()
        s['window_width'] = 200
        s['window_height'] = 200
        s['num_points'] = 10000
        s['pixel_scale'] = .532
        return s

    def gui(self):
        self.gui_reset()
        window_width = SliderLabel()
        window_width.setRange(1, 2000)
        window_height = SliderLabel()
        window_height.setRange(1, 2000)
        num_points = SliderLabel()
        num_points.setRange(1, 13000)
        pixel_scale = QtWidgets.QDoubleSpinBox()
        pixel_scale.setDecimals(3)
        pixel_scale.setSingleStep(.001)
        self.items.append({'name': 'window_width', 'string': 'Window Width', 'object': window_width})
        self.items.append({'name': 'window_height', 'string': 'Window Height', 'object': window_height})
        self.items.append({'name': 'num_points', 'string': 'Number of Points', 'object': num_points})
        self.items.append({'name': 'pixel_scale', 'string': 'Microns per Pixel', 'object': pixel_scale})
        super().gui()
        self.ui.setGeometry(QRect(400, 50, 600, 130))

    def __call__(self, window_width=200, window_height=200, num_points=10000, pixel_scale=.532):
        try:
            self.start()
            export_text = ''
            random_x = np.random.uniform(0, window_width, num_points)
            random_y = np.random.uniform(0, window_height, num_points)
            for i, k in zip(random_x, random_y):
                export_text += str(i) + ' ' + str(k) + '\n'
            area = 5
            plt.scatter(random_x, random_y, s=area)
            plt.show()
            save_box = QMessageBox()
            save_box.setWindowTitle('Save?')
            save_box.setText('Save (x,y) coordinates of scatter plot? This is necessary to compute nearest neighbors.')
            save_box.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
            save_box.setDefaultButton(QMessageBox.Save)
            ret = save_box.exec_()
            if ret == QMessageBox.Save:
                r = save_text_file(export_text)
                compute_neighbor_distance(r[0], r[1])
            else:
                return
        except TypeError:
            return

PointSim = PointSim()
