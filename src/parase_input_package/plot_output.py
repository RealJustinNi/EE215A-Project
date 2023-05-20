from PIL import Image,ImageDraw
import numpy as np
def plot_path(save_path,columns,rows,block_list,path_dict):
    #size = int(1024/max(columns,rows))
    size = 20
    background = Image.new('RGB', (columns*size,rows*size), (255, 255, 255))
    blue  =  Image.new('RGB', (size, size), (70, 73, 156))
    red   =  Image.new('RGB', (size, size), (195, 56, 40))
    black =  Image.new('RGB', (size, size), (33, 25, 24))
    draw = ImageDraw.Draw(background)
    for item in block_list:
        background.paste(black,(item[0]*size,item[1]*size))
    for key in path_dict.keys():
        for item in path_dict[key]:
            if (path_dict[key].index(item) == 0) or (path_dict[key].index(item) == len(path_dict[key]) - 1):
                background.paste(blue,(item[0]*size,item[1]*size))
            else:
                background.paste(red,(item[0]*size,item[1]*size))
            draw.text((item[0]*size+int(0.25*size),item[1]*size+int(0.25*size)), str(key), fill=(255, 255, 255))
    #background.rotate(90).save(save_path) 
    background.save(save_path) 

def plot_problem(save_path,columns,rows,grid,netlist):
    #size = int(1024/max(columns,rows))
    size = 20
    background = Image.new('RGB', (columns*size,rows*size), (255, 255, 255))
    blue  =  Image.new('RGB', (size, size), (70, 73, 156))
    red   =  Image.new('RGB', (size, size), (195, 56, 40))
    black =  Image.new('RGB', (size, size), (33, 25, 24))
    draw = ImageDraw.Draw(background)
    block_list = np.argwhere(grid.T==-1)
    grid_cost = np.argwhere(grid.T>=1)
    for item in block_list:
        background.paste(black,(item[0]*size,item[1]*size))
    for item in grid_cost:
        draw.text((item[0]*size+int(0.25*size),item[1]*size+int(0.25*size)), str(int(grid.T[item[0]][item[1]])), fill=(0, 0, 0))
    for item in netlist:
        background.paste(blue,(item['pin1']['x']*size,item['pin1']['y']*size))
        background.paste(blue,(item['pin2']['x']*size,item['pin2']['y']*size))
        draw.text((item['pin1']['x']*size+int(0.25*size),item['pin1']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
        draw.text((item['pin2']['x']*size+int(0.25*size),item['pin2']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
    #background.rotate(90).save(save_path) 
    background.save(save_path) 