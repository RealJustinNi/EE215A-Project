import numpy as np
from io import StringIO

def parse_gridfile_evaluate(filepath):
    f=open(filepath)
    data = []
    for line in f:
        data.append(line.strip())
    f.close()
    columns = int(data[0].split(" ",4)[0])
    rows = int(data[0].split(" ",4)[1])
    bend_penalty = int(data[0].split(" ",4)[2])
    via_penalty = int(data[0].split(" ",4)[3])
    print("bend_penalty:",bend_penalty,"\n","via_penalty:",via_penalty)
    string = str(data[1:])
    for item in ["'","[","]",","]:
        string=string.replace(item,"")
    array = np.genfromtxt(StringIO(string))
    array = array.reshape((2*rows,columns))
    layer1_gird,layer2_grid = np.vsplit(array, 2)[0],np.vsplit(array, 2)[1]
    return bend_penalty,via_penalty,layer1_gird,layer2_grid


def parse_netlist_evaluate(filepath):
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
    return nets,net_count

def read_output_file(file_path):
    paths = []  # 用于存储所有路径数据
    missing_net_ids = []  # 用于存储没有路径的 net_id
    with open(file_path, 'r') as file:
        net_number = int(file.readline().strip())
        for _ in range(net_number):
            net_id = int(file.readline().strip())
            path = []
            line = file.readline().strip()
            if line == '0':
                missing_net_ids.append(net_id)
            else:
                while line != '0':
                    layer_info, x_coord, y_coord = map(int, line.split())
                    path.append({'layer': layer_info, 'x': x_coord, 'y': y_coord})
                    line = file.readline().strip()
                paths.append({'net_id': net_id, 'path': path})  # 将路径数据添加到 paths 列表中
    if missing_net_ids:
        for net_id in missing_net_ids:
            print(f"没有布线的节点: {net_id}")
    else:
        print("所有的节点均已布线.")
    return paths, missing_net_ids

def check_duplicate_points(output_data):
    visited_points = set()
    duplicate_points = {}
    for net in output_data:
        net_id = net['net_id']
        for point in net['path']:
            x = point['x']
            y = point['y']
            layer = point['layer']
            point_tuple = (x, y, layer)
            if point_tuple in visited_points:
                if point_tuple in duplicate_points:
                    duplicate_points[point_tuple].append(net_id)
                else:
                    duplicate_points[point_tuple] = [net_id]
            else:
                visited_points.add(point_tuple)
    
    if len(duplicate_points) > 0:
        print("存在重复的点:")
        for point, net_ids in duplicate_points.items():
            print(f"X: {point[0]}, Y: {point[1]}, Layer: {point[2]}")
            print("重复的Net ID:", net_ids)
    else:
        print("未找到重复的点。")
    
    return duplicate_points


def check_adjacent_points(path):
    for i in range(len(path) - 1):
        current_point = path[i]
        next_point = path[i + 1]
        diff_count = 0
        if current_point['x'] != next_point['x']:
            diff_count += 1
        if current_point['y'] != next_point['y']:
            diff_count += 1
        if current_point['layer'] != next_point['layer']:
            diff_count += 1
        if diff_count != 1:
            return False
    return True

def check_adjacent_paths(paths):
    incorrect_paths = []  # 存储不正确的路径的 ID
    for data in paths:
        path = data['path']
        is_adjacent = check_adjacent_points(path)
        if not is_adjacent:
            incorrect_paths.append(data['net_id'])
    if len(incorrect_paths) > 0:
        print("不连续布线的Net ID:",incorrect_paths)
    else:
        print("所有布线都连续")
    return


def check_path_coordinates(paths, nets):
    matching_paths = []  # 用于存储匹配的路径数据
    for path_data in paths:
        net_id = path_data['net_id']
        path = path_data['path']
        net = next((net for net in nets if net['net_id'] == net_id), None)
        if net is None:
            print(f"无法找到匹配的网络列表数据,Net ID: {net_id}")
        else:
            pin1 = net['pin1']
            pin2 = net['pin2']
            path_start = path[0]
            path_end = path[-1]
            if (path_start['layer'], path_start['x'], path_start['y']) != (pin1['layer'], pin1['x'], pin1['y']):
                print(f"路径起点与网络列表不匹配，Net ID: {net_id}")
            #else:
            #    print(f"路径起点与网络列表匹配，Net ID: {net_id}")
            if (path_end['layer'], path_end['x'], path_end['y']) != (pin2['layer'], pin2['x'], pin2['y']):
                print(f"路径终点与网络列表不匹配，Net ID: {net_id}")
            else:
                matching_paths.append(path_data)  # 添加匹配的路径数据到列表中

    if len(matching_paths) == len(paths):
        print("布线结果的起点和终点与Nets全部匹配")
    else:
        print("布线结果的起点和终点与Nets发现不匹配")
        
def calculate_path_cost(paths, bend_penalty, via_penalty, layer1_grid, layer2_grid):
    total_cost = 0
    cost_path = {}
    for path in paths:
        net_id = path['net_id']
        path_data = path['path']
        cost_path[net_id] = 0
        cost = 0
        # 计算每个点的成本
        for i, point in enumerate(path_data):
            
            x = point['x']
            y = point['y']
            layer = point['layer']

            if layer == 1 or layer == 2:
                # 加上 layer1/2_grid 上对应 (x, y) 的值
                cost += layer1_grid[x][y] if layer == 1 else layer2_grid[x][y]
            elif layer == 3:
                cost += via_penalty
            if i > 1:
                # 计算路径弯曲的成本
                prev_prev_layer = path_data[i - 2]['layer']
                prev_prev_x = path_data[i - 2]['x']
                prev_prev_y = path_data[i - 2]['y']
                prev_layer = path_data[i - 1]['layer']
                if prev_prev_layer == layer and prev_layer == layer and (prev_prev_x != x and y != prev_prev_y):
                    cost += bend_penalty
        cost_path[net_id]=cost
        total_cost += cost
    print("total_cost:",total_cost)               
    return cost_path,total_cost


def evaluate_route(router_path,bench_name):
    paths,_ = read_output_file(router_path)
    duplicate_points = check_duplicate_points(paths)
    check_adjacent_paths(paths)
    netlist_file_path = '../benchmark/'+bench_name+'.nl'
    gridfile_path  = '../benchmark/'+bench_name+'.grid'
    nets,_ = parse_netlist_evaluate(netlist_file_path)
    bend_penalty,via_penalty,layer1_grid,layer2_grid = parse_gridfile_evaluate(gridfile_path)
    check_path_coordinates(paths, nets)
    cost_path,total_cost=calculate_path_cost(paths, bend_penalty, via_penalty, layer1_grid.T, layer2_grid.T)
    return duplicate_points ,cost_path,total_cost


'''
 调用方式
 from parase_input_package.evaluate import *
 router_path = '../output/bench4.router'
 bench_name ="bench4"
 duplicate_points ,cost_path,total_cost=evaluate_route(router_path,bench_name)  
'''