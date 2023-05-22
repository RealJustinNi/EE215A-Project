def generate_output_file(filepath, net_number, routing_paths):
    with open(filepath, 'w') as file:
        file.write(str(net_number) + '\n')
        for net_id, routing_path in routing_paths.items():
            file.write(str(net_id) + '\n')
            prev_x,prev_y,prev_layer = None,None,None
            if routing_path:  # None的情况
                for  x, y,layer in routing_path:
                    if prev_layer!= layer and prev_x == x and prev_y == y:
                        file.write('3 ' + str(prev_x) + ' ' + str(prev_y) + '\n')  # Write via cell
                    file.write(str(layer) + ' ' + str(x) + ' ' + str(y) + '\n')
                    prev_x, prev_y, prev_layer = x, y, layer
            file.write('0\n')