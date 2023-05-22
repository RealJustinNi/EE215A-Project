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
        if path_dict[key]:
            for item in path_dict[key]:
                if (path_dict[key].index(item) == 0) or (path_dict[key].index(item) == len(path_dict[key]) - 1):
                    background.paste(blue,(item[0]*size,item[1]*size))
                else:
                    background.paste(red,(item[0]*size,item[1]*size))
                if key <100:
                    draw.text((item[0]*size+int(0.25*size),item[1]*size+int(0.25*size)), str(key), fill=(255, 255, 255))
                elif key >= 100:
                    draw.text((item[0]*size,item[1]*size+int(0.25*size)), str(key), fill=(255, 255, 255))
    #background.rotate(90).save(save_path) 
    background.save(save_path) 

def plot_problem(save_path,columns,rows,grid1,grid2,netlist):
    size = 20
    background1 = Image.new('RGB', (columns*size,rows*size), (255, 255, 255))
    background2 = Image.new('RGB', (columns*size,rows*size), (255, 255, 255))
    blue  =  Image.new('RGB', (size, size), (70, 73, 156))
    black =  Image.new('RGB', (size, size), (33, 25, 24))
    draw1,draw2 = ImageDraw.Draw(background1),ImageDraw.Draw(background2)
    block_list1,block_list2 = np.argwhere(grid1.T==-1),np.argwhere(grid2.T==-1)
    grid_cost1,grid_cost2 = np.argwhere(grid1.T>=1),np.argwhere(grid2.T>=1)
    # 画第一层的障碍物
    for item in block_list1:
        background1.paste(black,(item[0]*size,item[1]*size))
    # 画第一层的单元cost
    for item in grid_cost1:
        draw1.text((item[0]*size+int(0.25*size),item[1]*size+int(0.25*size)), str(int(grid1.T[item[0]][item[1]])), fill=(0, 0, 0))
    # 画第二层的障碍物
    for item in block_list2:
        background2.paste(black,(item[0]*size,item[1]*size))
    # 画第二层的单元cost
    for item in grid_cost2:
        draw2.text((item[0]*size+int(0.25*size),item[1]*size+int(0.25*size)), str(int(grid2.T[item[0]][item[1]])), fill=(0, 0, 0))

    for item in netlist:
        if item['pin1']['layer']==1:
            background1.paste(blue,(item['pin1']['x']*size,item['pin1']['y']*size))
            if int(item['net_id'])<100:
                draw1.text((item['pin1']['x']*size+int(0.25*size),item['pin1']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
            else:
                draw1.text((item['pin1']['x']*size,item['pin1']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
        if item['pin2']['layer']==1:
            background1.paste(blue,(item['pin2']['x']*size,item['pin2']['y']*size))
            if int(item['net_id'])<100:
                draw1.text((item['pin2']['x']*size+int(0.25*size),item['pin2']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
            else:
                draw1.text((item['pin2']['x']*size,item['pin2']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
        if item['pin1']['layer']==2:
            background2.paste(blue,(item['pin1']['x']*size,item['pin1']['y']*size))
            if int(item['net_id'])<100:
                draw2.text((item['pin1']['x']*size+int(0.25*size),item['pin1']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
            else:
                draw2.text((item['pin1']['x']*size,item['pin1']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
        if item['pin2']['layer']==2:
            background2.paste(blue,(item['pin2']['x']*size,item['pin2']['y']*size))
            if int(item['net_id'])<100:
                draw2.text((item['pin2']['x']*size+int(0.25*size),item['pin2']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))
            else:
                draw2.text((item['pin2']['x']*size,item['pin2']['y']*size+int(0.25*size)), str(int(item['net_id'])), fill=(255, 255, 255))

    background1.save(save_path[:-4]+'_layer1.jpg') 
    background2.save(save_path[:-4]+'_layer2.jpg') 