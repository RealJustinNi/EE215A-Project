from PIL import Image,ImageDraw
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