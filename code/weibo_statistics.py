# -*- coding: utf-8 -*-

import sys
sys.path.append('../tranpotation_experiment/code/_utils')
from _const import _grid_width, _grid_height, _cube_width, _cube_height, inbound, XY2cord, cord2XY, cord2gridXY, gridXY2mapXY
from _colors import _color_red_list, _color_orange_list, get_color

import fileinput
from pylab import *

def basic_statistics(statistic_type = 'entry'):
    _matrix_entry = [[0 for y in range(_grid_height)] for x in range(_grid_width)]
    _matrix_location = [[{} for y in range(_grid_height)] for x in range(_grid_width)]
    for line in fileinput.input('_data/data.txt'):
        _, _date, _location, _, _content = line.strip().split('\t')
        _location_name, _coordinate = _location.split('|')
        _lng, _lat = _coordinate.split(',')
        _lng, _lat = float(_lng), float(_lat)
        if inbound(_lng, _lat):
            _gx, _gy = cord2gridXY(_lng, _lat)
            _matrix_entry[_gx][_gy] += 1
            _matrix_location[_gx][_gy][_location_name] = True
    fileinput.close()
    _matrix_location = [[len(_matrix_location[x][y].keys()) 
                            for y in range(_grid_height)] for x in range(_grid_width)]
    fig, ax = plt.subplots(1,subplot_kw={'xticks': [], 'yticks': []})
    image = plt.imread('../tranpotation_experiment/result/_map_bounds/shanghai_nokia.png')
    ax.imshow(image)
    if statistic_type == 'entry':
        _matrix = np.array(_matrix_entry)
    if statistic_type == 'location':
        _matrix = np.array(_matrix_location)
    _min, _max = _matrix.min(), _matrix.max()
    for x in range(_grid_width):
        for y in range(_grid_height):
            cube_color = get_color(_color_orange_list, _min, _max, _matrix[x][y])
            if cube_color != '#ffffff':
                cube = plt.Rectangle(gridXY2mapXY(x,y), _cube_width, _cube_height, fc=cube_color, alpha=0.6, linewidth=0)
                ax.add_patch(cube)
    plt.savefig("./_result/shanghai_weibo_{}_distribution_nokia.png".format(statistic_type))

# basic_statistics('entry')
# basic_statistics('location')
