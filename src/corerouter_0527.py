from parase_input_package.generate_output import *
from parase_input_package.parase_input import *
from parase_input_package.plot_output import *
import argparse
import time
from parase_input_package.evaluate import *

parser = argparse.ArgumentParser()
parser.add_argument('-f','--filename', type=str,choices=["bench1","bench2","bench3","bench4","bench5","fract2","industry1","primary1"])
parser.add_argument('-i','--iteration', type=int)
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

def reconstruct_path_tmp(source, target_tmp, parents):
    path_tmp = []
    current = target_tmp
    while current != source and len(path_tmp)<=3:
        path_tmp.append(current)
        current = parents[current]
    path_tmp.append(source)
    path_tmp.reverse()
    return path_tmp

def mark_path_on_grid(layer1_grid,layer2_grid, path):
    if path:              
        for cell in path:
            x, y, layer = cell
            if layer == 1:
                layer1_grid[x][y] = -1
            else:
                layer2_grid[x][y] = -1
def judge_bend(path_tmp,cell):
    cnt = 0
    list = path_tmp.copy()
    list.append(cell)
    if list:
        for i in range(1,len(list)+1):
            layer = list[-1][2]
            tmp = list[-1][1] if layer==1 else list[-1][0]
            current = list[-1*i][1] if layer==1 else list[-1*i][0]
            if list[-1*i][2] == layer and current==tmp:
                cnt+=1
            else:
                break
    return cnt
def get_cell_cost(layer_grid, cell,path_tmp,bend_penalty,via_penalty,advanced):  
    x, y, layer = cell
    cell_cost = 1  # 默认的单元代价
    if layer_grid[x][y] == -1:
        cell_cost = float('inf')  # -1表示无法通过的细胞
    elif layer_grid[x][y] != 1:
        cell_cost = layer_grid[x][y]  # 非单元代价
    if advanced==False:
        if path_tmp:
            last_x,last_y,last_layer = path_tmp[-1]
            if layer != last_layer:
                cell_cost += via_penalty
            elif len(path_tmp) >= 2:
                prev_cell = path_tmp[-2]
                prev_x, prev_y, prev_layer = prev_cell
                if (prev_x != x and prev_y != y):  
                    cell_cost += bend_penalty
    elif path_tmp:
        last_x,last_y,last_layer = path_tmp[-1]
        if layer != last_layer:
            cell_cost += via_penalty
        else: 
            cnt = judge_bend(path_tmp,cell)
            if cnt> 1:
                cell_cost += bend_penalty * (cnt-1)
            if len(path_tmp) >= 2:
                prev_cell = path_tmp[-2]
                prev_x, prev_y, prev_layer = prev_cell
                if (prev_x != x and prev_y != y):  
                    cell_cost += bend_penalty
    return cell_cost

def expand_source_to_target(rows, columns, layer1_grid,layer2_grid, source, target,bend_penalty,via_penalty,advanced,single_enable,iteration,eta):
    s1 = time.time()
    wavefront = {}
    visited = set()
    parents = {}
    costs = {}  # Store the cumulative costs for each cell
    
    source_tuple = (source['x'], source['y'], source['layer'])
    target_tuple = (target['x'], target['y'], target['layer'])
    
    wavefront[source_tuple] = 0
    costs[source_tuple] = 1  # Initial cost for the source cell is 1
    while wavefront:
        if (time.time() - s1 >= 20+int(iteration/2)) and advanced:
            return None,None

        # get lowest cost cell on a wavefront structure
        current_cell = sorted(wavefront.items(),key=lambda s:int(s[1]))[0][0]

        if current_cell == target_tuple:
            path = reconstruct_path(source_tuple, target_tuple, parents)
            return path,costs[current_cell]

        if single_enable:
            #neighbors = get_neighbors_different_directions(rows, columns, current_cell,layer1_grid,layer2_grid)  
            neighbors = get_neighbors(rows, columns, current_cell,layer1_grid,layer2_grid)  
        else:
            neighbors = get_neighbors(rows, columns, current_cell,layer1_grid,layer2_grid)
        
        for neighbor in neighbors:
            neighbor_tuple = (neighbor['x'], neighbor['y'], neighbor['layer'])

            if neighbor_tuple not in visited:
                #path_tmp= reconstruct_path_tmp(source_tuple, current_cell, parents)
                path_tmp= reconstruct_path(source_tuple, current_cell, parents)
                # Calculate the cost to reach the neighbor cell
                if(neighbor_tuple[2]== 1):
                  cost = costs[current_cell] + get_cell_cost(layer1_grid, neighbor_tuple,path_tmp,bend_penalty,via_penalty,advanced)
                else:
                  cost = costs[current_cell] + get_cell_cost(layer2_grid, neighbor_tuple,path_tmp,bend_penalty,via_penalty,advanced)
                # ignore blocks
                if cost!= np.inf:
                    if neighbor_tuple not in wavefront.keys() or costs[neighbor_tuple] > cost:
                        costs[neighbor_tuple] = cost
                        parents[neighbor_tuple] = current_cell

                    #if neighbor_tuple not in wavefront.keys():   0529
                        # add cell N to waveform, indexed by pathcost
                        if advanced == False and single_enable == False:
                            cost_target = cost
                        elif advanced == False and single_enable == True:
                            cost_target = cost + via_penalty*abs(neighbor_tuple[2]-target_tuple[2])*eta
                            cost_target += (abs(neighbor_tuple[0]-target_tuple[0])+abs(neighbor_tuple[1]-target_tuple[1]))*via_penalty*eta
                        elif advanced == True and single_enable == True:
                            cost_target = cost + via_penalty*abs(neighbor_tuple[2]-target_tuple[2])*eta
                            cost_target += (abs(neighbor_tuple[0]-target_tuple[0])+abs(neighbor_tuple[1]-target_tuple[1]))*via_penalty*eta
                        elif advanced == True and single_enable == False:
                            cost_target = cost + via_penalty*abs(neighbor_tuple[2]-target_tuple[2])
                        wavefront[neighbor_tuple]=cost_target          

        visited.add(current_cell)    
        del wavefront[current_cell]                  
    return None,None

def get_neighbors(rows, columns, cell,layer1_grid,layer2_grid): 
    x, y, layer = cell
    neighbors = []
    if y > 0:
        if (layer == 1 and layer1_grid[x][y-1] !=-1) or (layer == 2 and layer2_grid[x][y-1] !=-1):
            neighbors.append({'x': x, 'y': y - 1, 'layer': layer})
    if x < columns - 1:
        if (layer == 1 and layer1_grid[x+1][y] !=-1) or (layer == 2 and layer2_grid[x+1][y] !=-1):
            neighbors.append({'x': x + 1, 'y': y, 'layer': layer})
    if y < rows - 1:
        if (layer == 1 and layer1_grid[x][y+1] !=-1) or (layer == 2 and layer2_grid[x][y+1] !=-1):
            neighbors.append({'x': x, 'y': y + 1, 'layer': layer})
    if x > 0:
        if (layer == 1 and layer1_grid[x-1][y] !=-1) or (layer == 2 and layer2_grid[x-1][y] !=-1):
            neighbors.append({'x': x - 1, 'y': y, 'layer': layer})
    if (layer == 1 and layer2_grid[x][y] !=-1) or (layer == 2 and layer1_grid[x][y] !=-1):     
        neighbors.append({'x': x, 'y': y, 'layer': 3-layer})                                            
    return neighbors

def get_neighbors_different_directions(rows, columns, cell,layer1_grid,layer2_grid): 
    x, y, layer = cell
    neighbors = []
    if y > 0:
        if (layer == 1 and layer1_grid[x][y-1] !=-1) :
            neighbors.append({'x': x, 'y': y - 1, 'layer': layer})
    if x < columns - 1:
        if (layer == 2 and layer2_grid[x+1][y] !=-1):
            neighbors.append({'x': x + 1, 'y': y, 'layer': layer})
    if y < rows - 1:
        if (layer == 1 and layer1_grid[x][y+1] !=-1) :
            neighbors.append({'x': x, 'y': y + 1, 'layer': layer})
    if x > 0:
        if  (layer == 2 and layer2_grid[x-1][y] !=-1):
            neighbors.append({'x': x - 1, 'y': y, 'layer': layer})
    if (layer == 1 and layer2_grid[x][y] !=-1) or (layer == 2 and layer1_grid[x][y] !=-1):     
        neighbors.append({'x': x, 'y': y, 'layer': 3-layer})                                            
    return neighbors

def true_two_layer_router(rows, columns, layer1_grid,layer2_grid, nets,bend_penalty,via_penalty,advanced,single_enable,iteration):
    cnt_ire = 0
    have_result = 0
    bad_net = []
    bad_net_cnt = []
    best = 99999999
    nets.sort(key=lambda s: ((s["pin1"]['x']-s["pin2"]['x'])**2+(s["pin1"]['y']-s["pin2"]['y'])**2)+(s["pin1"]['layer']-s["pin2"]['layer'])**2)
    nets_difficult = nets[-1*int(0.1*len(nets)):]
    nets_difficult.reverse()
    nets = nets_difficult+(nets[:-1*int(0.1*len(nets))])
    bad_net_tmp = []
    #print(advanced,single_enable)
    if len(nets) == 1000:
        eta = 0.5 + 0.025
    else:
        eta = 0.25 + 0.0125
    
    while (bad_net_tmp != [] or cnt_ire==0 or have_result ==1 ) and cnt_ire<iteration-1:
        print('Iteration:'+str(cnt_ire))
        if (len(bad_net_cnt) < 2) or (bad_net_cnt[-1] <= bad_net_cnt[-2]):
            if len(nets) == 1000:
                eta = eta - 0.025
            else:
                eta = eta-0.0125
        else:
            eta = eta
        print('eta:'+str(eta))
     
        for item in bad_net:
            net_bad = nets.pop(nets.index(item))
            nets.insert(0,net_bad)
        bad_net_tmp = []
        routing_table = {}
        costs_table = {}
        delta_table = {}
        cnt_ire +=1
        cnt = 0
        layer1_ori,layer2_ori=layer1_grid.copy(),layer2_grid.copy()
        for net in nets:
            net_id = net['net_id']
            pin1 = net['pin1']
            pin2 = net['pin2']
            # 防止布线在后续的pin上，先将所有的pin标记为-1；
            if pin1['layer'] == 1:
                layer1_ori[pin1['x']][pin1['y']] = -1
            if pin1['layer'] == 2:
                layer2_ori[pin1['x']][pin1['y']] = -1
            if pin2['layer'] == 1:
                layer1_ori[pin2['x']][pin2['y']] = -1
            if pin2['layer'] == 2:
                layer2_ori[pin2['x']][pin2['y']] = -1
            
        for net in nets:
            net_id = net['net_id']
            pin1 = net['pin1']
            pin2 = net['pin2']
            if pin1['layer'] == 1:
                layer1_ori[pin1['x']][pin1['y']] = 1
            if pin1['layer'] == 2:
                layer2_ori[pin1['x']][pin1['y']] = 1
            if pin2['layer'] == 1:
                layer1_ori[pin2['x']][pin2['y']] = 1
            if pin2['layer'] == 2:
                layer2_ori[pin2['x']][pin2['y']] = 1
            cnt += 1
            print('Routing net:',net_id,'\t ('+str(cnt)+'/'+str(len(nets))+')')

            path,costs = expand_source_to_target(rows, columns, layer1_ori,layer2_ori, pin1, pin2,bend_penalty,via_penalty,advanced,single_enable,iteration=cnt_ire,eta=eta)
            
            if path is not None:
                mark_path_on_grid(layer1_ori,layer2_ori,path)
                routing_table[net_id] = path
                costs_table[net_id] = costs
            else:
                cnt -= 1
                print('This net will be re-routed again:',net_id)
                bad_net_tmp.append(net)
                routing_table[net_id] = None
                costs_table[net_id] = None
                if pin1['layer'] == 1:
                    layer1_ori[pin1['x']][pin1['y']] = -1
                if pin1['layer'] == 2:
                    layer2_ori[pin1['x']][pin1['y']] = -1
                if pin2['layer'] == 1:
                    layer1_ori[pin2['x']][pin2['y']] = -1
                if pin2['layer'] == 2:
                    layer2_ori[pin2['x']][pin2['y']] = -1
        bad_net +=bad_net_tmp
        bad_net_cnt.append(len(bad_net_tmp))
        if bad_net_tmp == [] and routing_table:
            have_result = 1
            if best > sum(costs_table.values()):
                best = sum(costs_table.values())
                best_routing_table = routing_table
                best_costs_table = costs_table
        else:
            have_result = 0
            
    return best_routing_table,best_costs_table


if __name__ == "__main__":
    print('Parsing',args.filename,'...')
    filepath_out='../out/'+args.filename+'_0526.router'
    netlist_file_path = '../benchmark/'+args.filename+'.nl'
    gridfile_path  = '../benchmark/'+args.filename+'.grid'
    nets,net_num = parse_netlist(netlist_file_path)
    rows,columns,bend_penalty,via_penalty,layer1_grid_original,layer2_grid_original = parse_gridfile(gridfile_path)
    plot_problem('../out/figure/'+args.filename+'_problem.jpg',columns,rows,layer1_grid_original,layer2_grid_original,nets)
    layer1_grid = layer1_grid_original.copy()
    layer2_grid = layer2_grid_original.copy()
    if args.filename in ["bench1","bench2","bench3","bench4"]:
        single_enable = False
        advanced = False
    elif args.filename in ["bench5","fract2"]:
        single_enable = True
        advanced = True
    elif args.filename in ["primary1","industry1"]:
        single_enable = True
        advanced = True
    s_time = time.time()
    if single_enable:
        if args.iteration:
            routing_table,costs_table=true_two_layer_router(rows, columns, layer1_grid.T,layer2_grid.T, nets,bend_penalty,via_penalty,advanced,single_enable,iteration=args.iteration)
        else:
            routing_table,costs_table=true_two_layer_router(rows, columns, layer1_grid.T,layer2_grid.T, nets,bend_penalty,via_penalty,advanced,single_enable,iteration=20)
    else:
        routing_table,costs_table=true_two_layer_router(rows, columns, layer1_grid.T,layer2_grid.T, nets,bend_penalty,via_penalty,advanced,single_enable,iteration=1)
    routing_table = dict(sorted(routing_table.items(),key=lambda x:x[0]))
    print('All routing time:'+str(time.time()-s_time)[0:5]+'s')
    print('Required routing nets:'+str(len(nets)))
    print('Finished routing nets:'+str(len(routing_table)))
    for key in list(costs_table.keys()):
        if not costs_table.get(key):
            del costs_table[key]
    costs_table = dict(sorted(costs_table.items(),key=lambda x:x[0]))
    print('Overall cost:'+str(sum(costs_table.values())))
    plot_path('../out/figure/'+args.filename+'_result.jpg',columns=columns,rows=rows,grid1=layer1_grid_original,grid2=layer2_grid_original,path_dict=routing_table) 
    generate_output_file(filepath_out,net_num,routing_table)