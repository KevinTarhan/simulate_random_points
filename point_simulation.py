import numpy as np
from qtpy import QtWidgets
import flika
flika_version = flika.__version__
from flika import global_vars as g
from flika.process.BaseProcess import BaseProcess_noPriorWindow, SliderLabel, CheckBox
from flika.process.file_ import save_file_gui, open_file_gui
from qtpy.QtWidgets import *
from qtpy.QtCore import *
import os.path
import matplotlib.pyplot as plt
from matplotlib import path
from .neighbor_dist import distances
from flika.logger import logger
from matplotlib.widgets import LassoSelector


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


def get_text_file(filename=None):
    if filename is None:
            filetypes = '.txt'
            prompt = 'Open File'
            filename = open_file_gui(prompt, filetypes=filetypes)
            if filename is None:
                return None
    else:
        filename = g.settings['filename']
        if filename is None:
            g.alert('No filename selected')
            return None
    print("Filename: {}".format(filename))
    g.m.statusBar().showMessage('Loading {}'.format(os.path.basename(filename)))
    return filename


def bounded_point_sim(width,height,numpoints,boundaries, pixel_scale, display_graphs):
    random_x = []
    random_y = []
    export_txt = ''
    np_bounds = np.loadtxt(boundaries, skiprows=1)
    comparison_path = path.Path(np_bounds)
    count = 0
    while count < numpoints:
        potential_x = np.random.uniform(0, width, 1)
        potential_y = np.random.uniform(0, height, 1)
        point_array = np.array([potential_x, potential_y]).reshape(1, 2)
        if comparison_path.contains_points(point_array):
            export_txt += str(potential_x[0] * pixel_scale) + ' ' + str(potential_y[0] * pixel_scale) + '\n'
            random_x.append(potential_x)
            random_y.append(potential_y)
            count += 1
    random_x = np.array(random_x)
    random_y = np.array(random_y)
    ret = save_plot_points(random_x, random_y, display_graphs)
    if ret == QMessageBox.Save:
        r = save_text_file(export_txt)
        compute_neighbor_distance(r[0], r[1], pixel_scale, display_graphs)
    else:
        return


def unbounded_point_sim(width,height,numpoints,pixel_scale,display_graphs):
    export_txt = ''
    random_x = np.random.uniform(0, width, numpoints)
    random_y = np.random.uniform(0, height, numpoints)
    for i, k in zip(random_x, random_y):
        export_txt += str(i * pixel_scale) + ' ' + str(k * pixel_scale) + '\n'
    ret = save_plot_points(random_x, random_y,display_graphs)
    if ret == QMessageBox.Save:
        r = save_text_file(export_txt)
        compute_neighbor_distance(r[0], r[1], pixel_scale, display_graphs)
    else:
        return


def save_plot_points(x,y,display_graphs, area=5):
    if display_graphs:
        plt.scatter(x, y, s=area)
        plt.show()
    save_box = QMessageBox()
    save_box.setWindowTitle('Save?')
    save_box.setText('Save (x,y) coordinates of scatter plot? This is necessary to compute nearest neighbors.')
    save_box.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
    save_box.setDefaultButton(QMessageBox.Save)
    ret = save_box.exec_()
    return ret


def compute_neighbor_distance(base_directory, file_directory, pixel_scale, display_graphs):
    save_box = QWidget()
    full_dir = r'{file}'.format(file=file_directory)
    file_output, ok = QInputDialog.getText(save_box, "Neighbor Distance", """Output filename?""")
    if not ok:
        return
    output_dir = r'{dir}/{file}.txt'.format(dir=base_directory, file=file_output)
    logger.debug(full_dir)
    distances(full_dir, full_dir, output_dir, pixel_scale, display_graphs)


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
        load_ROI = CheckBox()
        display_graphs = CheckBox()
        self.items.append({'name': 'window_width', 'string': 'Window Width', 'object': window_width})
        self.items.append({'name': 'window_height', 'string': 'Window Height', 'object': window_height})
        self.items.append({'name': 'num_points', 'string': 'Number of Points', 'object': num_points})
        self.items.append({'name': 'pixel_scale', 'string': 'Microns per Pixel', 'object': pixel_scale})
        self.items.append({'name': 'load_ROI', 'string': 'Load ROI?', 'object': load_ROI})
        self.items.append({'name': 'display_graphs', 'string': 'Display Graphs?', 'object': display_graphs})
        super().gui()
        self.ui.setGeometry(QRect(400, 50, 600, 130))

    def __call__(self, window_width=200, window_height=200, num_points=10000, pixel_scale=.532, load_ROI = False, display_graphs=True):
        try:
            if pixel_scale == 0:
                pixel_scale = 1
            self.start()
            if load_ROI:
                boundaries = get_text_file()
                bounded_point_sim(window_width, window_height, num_points, boundaries, pixel_scale,display_graphs)
            else:
                unbounded_point_sim(window_width, window_height, num_points, pixel_scale, display_graphs)
        except TypeError:
            return

PointSim = PointSim()



