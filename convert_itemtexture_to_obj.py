import sys
from PIL import Image

ALPHAHIGHPREF = 100

try:
    if sys.argv[2]:
        ALPHAHIGHPREF = int(sys.argv[2])
        if not ALPHAHIGHPREF:
            ALPHAHIGHPREF = 100
except:
    pass

def box(xmax, ymax, x, y, dval, around):

    faces = {
        "right": f"f {2+dval}/{3+(dval*1.5)} {1+dval}/{3+(dval*1.5)} {3+dval}/{2+(dval*1.5)} {4+dval}/{2+(dval*1.5)}",
        "left": f"f {8+dval}/{1+(dval*1.5)} {7+dval}/{1+(dval*1.5)} {5+dval}/{4+(dval*1.5)} {6+dval}/{4+(dval*1.5)}",
        "top": f"f {4+dval}/{4+(dval*1.5)} {3+dval}/{4+(dval*1.5)} {7+dval}/{3+(dval*1.5)} {8+dval}/{3+(dval*1.5)}",
        "lower": f"f {6+dval}/{2+(dval*1.5)} {5+dval}/{2+(dval*1.5)} {1+dval}/{1+(dval*1.5)} {2+dval}/{1+(dval*1.5)}"
    }

    incx = 1/xmax-0.01/xmax
    incy = 1/ymax-0.01/ymax
    xx = x/xmax
    yy = (y/ymax*-1+1-incy)-(0.01/ymax)
    addend = ''''''
    for dir in {"right", "left", "top", "lower"}:
        if around[dir] <= ALPHAHIGHPREF or not around[dir]:
            addend = addend+f'''
            #{dir}
            {faces[dir]}
            '''
    return f'''
    vt {xx} {yy+incy}
    vt {xx+incx} {yy+incy}
    vt {xx+incx} {yy}
    vt {xx} {yy}
    v {x+0.5} 0.5 {y-0.5}
    v {x+0.5} -0.5 {y-0.5}
    v {x+0.5} 0.5 {y+0.5}
    v {x+0.5} -0.5 {y+0.5}
    v {x-0.5} 0.5 {y-0.5}
    v {x-0.5} -0.5 {y-0.5}
    v {x-0.5} 0.5 {y+0.5}
    v {x-0.5} -0.5 {y+0.5}
    vt 0 0
    vt 0 0
    vt 0 0
    vt 0 0
    vt 0 0
    vt 0 0
    vt 0 0
    vt 0 0
    usemtl Material
    #top
    f {1+dval}/{1+(dval*1.5)} {5+dval}/{2+(dval*1.5)} {7+dval}/{3+(dval*1.5)} {3+dval}/{4+(dval*1.5)}
    #bottom
    f {6+dval}/{1+(dval*1.5)} {2+dval}/{2+(dval*1.5)} {4+dval}/{3+(dval*1.5)} {8+dval}/{4+(dval*1.5)}
    {addend}'''

def create_obj_file(image_path, output_path):
    image = Image.open(image_path)
    pixels = image.load()
    dval = 0
    with open(output_path+".mtl", 'w') as mtl_file:
        mtl_file.write(f'''newmtl Material
        Ns 0.000000
        Ka 1.000000 1.000000 1.000000
        Ks 0.500000 0.500000 0.500000
        Ke 0.000000 0.000000 0.000000
        Ni 1.450000
        d 1.000000
        illum 2
        map_Kd {image_path}''')
    with open(output_path+".obj", 'w') as obj_file:
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]

                around = {"right": 0, "left": 0, "top": 0, "lower": 0}

                if x < image.width-1:
                    n, n, n, around["right"] = pixels[x+1, y]
                if y < image.height-1:
                    n, n, n, around["top"] = pixels[x, y+1]
                if x != 0:
                    n, n, n, around["left"] = pixels[x-1, y]
                if y != 0:
                    n, n, n, around["lower"] = pixels[x, y-1]

                if a > ALPHAHIGHPREF:  # Non-transparent pixel
                    # Create a cube at the current pixel position
                    obj_file.write(f'''# Blender 4.0.2
                        # www.blender.org
                        mtllib {output_path}.mtl''')  # cube
                    obj_file.write(box(image.width,image.height,x,y,dval,around))  # cube
                    obj_file.write("s 0")  # cube
                    dval+=8

    print(f'OBJ file created: {output_path}')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <image_path> (optional <lowest_alpha>)")
        sys.exit(1)

    image_path = sys.argv[1]
    output_path = sys.argv[1]

    create_obj_file(image_path, output_path)
