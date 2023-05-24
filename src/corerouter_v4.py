from parase_input_package.generate_output import *
from parase_input_package.parase_input import *
from parase_input_package.plot_output import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f','--filename', type=str,choices=["bench1","bench2","bench3","bench4","bench5","fract2","industry1","primary1"])
args = parser.parse_args() 

def reconstruct_path(source, target, parents):
    path = []
    current = target
    while current != source:
        path.append(current)
        current = parents[current]
    path.append(source)
    path.reverse()
    return path

def mark_path_on_grid(layer1_grid, path):
    if path:               
        for cell in path:
            x, y, _ = cell
            layer1_grid[x][y] = -1

def get_cell_cost(layer_grid, cell,path_tmp,bend_penalty,via_penalty):  
    x, y, layer = cell
    cell_cost = 1  # 默认的单元代价
    if layer_grid[x][y] == -1:
        cell_cost = float('inf')  # -1表示无法通过的细胞
    elif layer_grid[x][y] != 1:
        cell_cost = layer_grid[x][y]  # 非单元代价
    if len(path_tmp) >= 2:
        prev_cell = path_tmp[-2]
        prev_x, prev_y, prev_layer = prev_cell
        if layer != prev_layer:
            cell_cost += via_penalty
        elif (prev_x != x and prev_y != y):  
            cell_cost += bend_penalty
    return cell_cost

def expand_source_to_target(rows, columns, layer1_grid,layer2_grid, source, target,bend_penalty,via_penalty):
    wavefront = {}
    visited = set()
    parents = {}
    costs = {}  # Store the cumulative costs for each cell
    
    source_tuple = (source['x'], source['y'], source['layer'])
    target_tuple = (target['x'], target['y'], target['layer'])
    
    wavefront[source_tuple] = 0
    costs[source_tuple] = 1  # Initial cost for the source cell is 1

    while wavefront:
        # get lowest cost cell on a wavefront structure
        current_cell = sorted(wavefront.items(),key=lambda s:int(s[1]))[0][0]

        if current_cell == target_tuple:
            path = reconstruct_path(source_tuple, target_tuple, parents)
            return path,costs[current_cell]

        neighbors = get_neighbors(rows, columns, current_cell)

        for neighbor in neighbors:
            neighbor_tuple = (neighbor['x'], neighbor['y'], neighbor['layer'])
            if neighbor_tuple not in visited:
                path_tmp= reconstruct_path(source_tuple, current_cell, parents)
                # Calculate the cost to reach the neighbor cell
                if(neighbor_tuple[2]== 1):
                  cost = costs[current_cell] + get_cell_cost(layer1_grid, neighbor_tuple,path_tmp,bend_penalty,via_penalty)
                if(neighbor_tuple[2]== 2):
                  cost = costs[current_cell] + get_cell_cost(layer2_grid, neighbor_tuple,path_tmp,bend_penalty,via_penalty)
                # ignore blocks
                if cost!= np.inf:
                    if neighbor_tuple not in wavefront.keys() or costs[neighbor_tuple] > cost:
                        costs[neighbor_tuple] = cost
                        parents[neighbor_tuple] = current_cell
                    if neighbor_tuple not in wavefront.keys():
                        # add cell N to waveform, indexed by pathcost
                        wavefront[neighbor_tuple]=cost         

        visited.add(current_cell)    
        del wavefront[current_cell]                  
    return None,None

def get_neighbors(rows, columns, cell):
    x, y, layer = cell
    neighbors = []
    if y < rows - 1:
        neighbors.append({'x': x, 'y': y + 1, 'layer': layer})
    if x < columns - 1:
        neighbors.append({'x': x + 1, 'y': y, 'layer': layer})
    if y > 0:
        neighbors.append({'x': x, 'y': y - 1, 'layer': layer})
    if x > 0:
        neighbors.append({'x': x - 1, 'y': y, 'layer': layer})     
    neighbors.append({'x': x, 'y': y, 'layer': 3-layer})                                          
    return neighbors

def true_two_layer_router(rows, columns, layer1_grid,layer2_grid, nets,bend_penalty,via_penalty):
    nets.sort(key=lambda s: ((s["pin1"]['x']-s["pin2"]['x'])**2+(s["pin1"]['y']-s["pin2"]['y'])**2))
    routing_table = {}
    costs_table = {}
    for net in nets:
        net_id = net['net_id']
        pin1 = net['pin1']
        pin2 = net['pin2']
        # 防止布线在后续的pin上，先将所有的pin标记为-1；
        if pin1['layer'] == 1:
            layer1_grid[pin1['x']][pin1['y']] = -1
        if pin1['layer'] == 2:
            layer2_grid[pin1['x']][pin1['y']] = -1
        if pin2['layer'] == 1:
            layer1_grid[pin2['x']][pin2['y']] = -1
        if pin2['layer'] == 2:
            layer2_grid[pin2['x']][pin2['y']] = -1
           
    for net in nets:
        net_id = net['net_id']
        pin1 = net['pin1']
        pin2 = net['pin2']
        if pin1['layer'] == 1:
            layer1_grid[pin1['x']][pin1['y']] = 1
        if pin1['layer'] == 2:
            layer2_grid[pin1['x']][pin1['y']] = 1
        if pin2['layer'] == 1:
            layer1_grid[pin2['x']][pin2['y']] = 1
        if pin2['layer'] == 2:
            layer2_grid[pin2['x']][pin2['y']] = 1
        print('Routing net:',net_id)
        path,costs = expand_source_to_target(rows, columns, layer1_grid,layer2_grid, pin1, pin2,bend_penalty,via_penalty) 
        if path is not None:
            mark_path_on_grid(layer1_grid,path)
            routing_table[net_id] = path
            costs_table[net_id] = costs
    routing_table = dict(sorted(routing_table.items(),key=lambda x:x[0]))
    costs_table = dict(sorted(costs_table.items(),key=lambda x:x[0]))
    return routing_table,costs_table


if __name__ == "__main__":
    print('Parsing',args.filename,'...')
    filepath_out='../out/'+args.filename+'.router'
    netlist_file_path = '../benchmark/'+args.filename+'.nl'
    gridfile_path  = '../benchmark/'+args.filename+'.grid'
    nets,net_num = parse_netlist(netlist_file_path)
    rows,columns,bend_penalty,via_penalty,layer1_grid_original,layer2_grid_original = parse_gridfile(gridfile_path)
    plot_problem('../out/figure/'+args.filename+'_problem.jpg',columns,rows,layer1_grid_original,layer2_grid_original,nets)
    layer1_grid = layer1_grid_original.copy()
    layer2_grid = layer2_grid_original.copy()
    routing_table,costs_table=true_two_layer_router(rows, columns, layer1_grid.T,layer2_grid.T, nets,bend_penalty,via_penalty)
    plot_path('../out/figure/'+args.filename+'_result.jpg',columns=columns,rows=rows,grid1=layer1_grid_original,grid2=layer2_grid_original,path_dict=routing_table) 
    generate_output_file(filepath_out,net_num,routing_table)