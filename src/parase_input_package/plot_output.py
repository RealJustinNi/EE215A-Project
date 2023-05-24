from PIL import Image,ImageDraw
import numpy as np

def show_number(key,item,draw1,draw2,size):
    # 路径上标字
    if key <100:
        if item[2]==1:
            draw1.text((item[0]*size+int(0.25*size),item[1]*size+int(0.25*size)), str(key), fill=(255, 255, 255))
        else:
            draw2.text((item[0]*size+int(0.25*size),item[1]*size+int(0.25*size)), str(key), fill=(255, 255, 255))
    elif key >= 100:
        if item[2]==1:
            draw1.text((item[0]*size,item[1]*size+int(0.25*size)), str(key), fill=(255, 255, 255))
        else:
            draw2.text((item[0]*size,item[1]*size+int(0.25*size)), str(key), fill=(255, 255, 255))    

def plot_path(save_path,columns,rows,grid1,grid2,path_dict):
    size = 20
    background1 = Image.new('RGB', (columns*size,rows*size), (255, 255, 255))
    background2 = Image.new('RGB', (columns*size,rows*size), (255, 255, 255))
    blue  =  Image.new('RGB', (size, size), (70, 73, 156))
    red   =  Image.new('RGB', (size, size), (195, 56, 40))
    black =  Image.new('RGB', (size, size), (33, 25, 24))
    green_r =  Image.new('RGB', (size, size), (195, 56, 40))
    draw_gr = ImageDraw.Draw(green_r)
    draw_gr.polygon(((3,3),(17,3),(17,17),(3,17)),fill=(124, 134, 65),outline=(124,134,65))
    green_b =  Image.new('RGB', (size, size), (70, 73, 156))
    draw_gb = ImageDraw.Draw(green_b)
    draw_gb.polygon(((3,3),(17,3),(17,17),(3,17)),fill=(124, 134, 65),outline=(124,134,65))

    draw1,draw2 = ImageDraw.Draw(background1),ImageDraw.Draw(background2)
    block_list1,block_list2 = np.argwhere(grid1.T==-1),np.argwhere(grid2.T==-1)
    # 画第一层的障碍物
    for item in block_list1:
        background1.paste(black,(item[0]*size,item[1]*size))
    # 画第二层的障碍物
    for item in block_list2:
        background2.paste(black,(item[0]*size,item[1]*size))
    
    previous = None
    for key in path_dict.keys():
        if path_dict[key]:
            for item in path_dict[key]:

                if (path_dict[key].index(item) == 0) or (path_dict[key].index(item) == len(path_dict[key]) - 1):
                    # 画source和target
                    if item[2]==1:
                        background1.paste(blue,(item[0]*size,item[1]*size))
                    else:
                        background2.paste(blue,(item[0]*size,item[1]*size))
                else:
                    # 画连线路径
                    if item[2]==1:
                        background1.paste(red,(item[0]*size,item[1]*size))
                    else:
                        background2.paste(red,(item[0]*size,item[1]*size))

                # 画打孔点
                if previous:
                    if (previous[0:2]==item[0:2]) and previous[2]!=item[2]:
                        if (path_dict[key].index(item) == 0) or (path_dict[key].index(item) == len(path_dict[key]) - 1):
                            background1.paste(green_b,(item[0]*size,item[1]*size))
                            background2.paste(green_b,(item[0]*size,item[1]*size))                    
                            show_number(key,previous,draw1,draw2,size)
                        else:
                            background1.paste(green_r,(item[0]*size,item[1]*size))
                            background2.paste(green_r,(item[0]*size,item[1]*size))
                            show_number(key,previous,draw1,draw2,size)
                show_number(key,item,draw1,draw2,size)      
                previous = item
    
    background1.save(save_path[:-4]+'_layer1.jpg') 
    background2.save(save_path[:-4]+'_layer2.jpg') 

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