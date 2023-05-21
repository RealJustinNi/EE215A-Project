def generate_output_file(filepath, net_number, routing_paths):
    with open(filepath, 'w') as file:
        file.write(str(net_number) + '\n')

        for net_id, routing_path in routing_paths.items():
            file.write(str(net_id) + '\n')
            for layer, x, y in routing_path:
                file.write(str(layer) + ' ' + str(x) + ' ' + str(y) + '\n')
            file.write('0\n')