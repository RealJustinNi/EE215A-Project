import numpy as np
from io import StringIO

def parse_gridfile(filepath):
    f=open(filepath)
    data = []
    for line in f:
        data.append(line.strip())
    f.close()
    columns = int(data[0].split(" ",4)[0])
    rows = int(data[0].split(" ",4)[1])
    bend_penalty = int(data[0].split(" ",4)[2])
    via_penalty = int(data[0].split(" ",4)[3])
    print(rows,columns,bend_penalty,via_penalty)
    string = str(data[1:])
    for item in ["'","[","]",","]:
        string=string.replace(item,"")
    array = np.genfromtxt(StringIO(string))
    array = array.reshape((2*rows,columns))
    layer1_gird,layer2_grid = np.vsplit(array, 2)[0],np.vsplit(array, 2)[1]
    print(layer1_gird.shape)
    print(layer2_grid.shape)
    return rows,columns,bend_penalty,via_penalty,layer1_gird,layer2_grid

def parse_netlist(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    net_count = int(lines[0])
    nets = []
    for i in range(1, net_count + 1):
        net_data = lines[i].split()
        net_id = int(net_data[0])
        pin1_layer = int(net_data[1])
        pin1_x = int(net_data[2])
        pin1_y = int(net_data[3])
        pin2_layer = int(net_data[4])
        pin2_x = int(net_data[5])
        pin2_y = int(net_data[6])
        net = {
            'net_id': net_id,
            'pin1': {'x': pin1_x, 'y': pin1_y, 'layer': pin1_layer},
            'pin2': {'x': pin2_x, 'y': pin2_y, 'layer': pin2_layer}
        }
        nets.append(net)
    return nets,net_count+1
