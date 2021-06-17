"""
    Simple tool to hide files inside images.
    Simply changes the 2 least significant bits of each pixel of an image to the
    bits of the hidden file. An indication of the file size is placed at the start
    of the least significant bits encoding so that the program knows when to stop
    decoding the file. The presence of a hidden file is easy to detect with noise
    level analysis so for any sort of real application (though there are next to
    no valid uses) some encryption on top of the steganographic hiding on files
    is preferable.
"""
from PIL import Image, UnidentifiedImageError
from sys import argv, exit
from numpy import asarray

def encode_image(image,payload):
    try:
        ims = str(image)
        im = Image.open(ims).convert("RGB")
    except FileNotFoundError:
        print(str(argv[0])+": \""+ims+"\": No such file or directory")
        return(1)
    except UnidentifiedImageError:
        print(str(argv[0])+": \""+ims+"\" is not a valid image file")
        return(1)

    try:
        fs = str(payload)
        f = open(fs,"rb")
        d = list(bytearray(f.read()))
        f.close()
    except FileNotFoundError:
        print(str(argv[0])+": \""+fs+"\": No such file or directory")

    w, h = im.size
    p = list(bytearray(im.tobytes()))
    
    fd = []
    ld = len(d)
    d = [ord(i) for i in str(len(d))]+[0x00]+d
    for a in d:
        fd+=[a>>0b110-i*0b10 &0b11 for i in range(0b100)] # Terribly written bitshifting garbage to place the payload in the 2 LSBs of the image

    if(len(fd)>len(p)):
        print(str(argv[0])+": data is too large to encode into image, get a bigger image or smaller data plz")
        return(1)

    for i in range(len(fd)):
        p[i]=(p[i]&0b11111100)+fd[i]

    p = bytes(p)
    nim = Image.frombytes("RGB", (w, h), p)
    nim.save("new_"+ims)

    print("Encoded file of length "+str(ld)+" bytes to new_"+ims)

def decode_image(image, outfile):
    try:
        ims = str(image)
        im = Image.open(ims).convert("RGB")
    except FileNotFoundError:
        print(str(argv[0])+": \""+ims+"\": No such file or directory")
        return(1)
    except UnidentifiedImageError:
        print(str(argv[0])+": \""+ims+"\" is not a valid image file")
        return(1)

    try:
        fs = str(outfile)
        f = open(fs,"wb")
    except FileNotFoundError:
        print(str(argv[0])+": \""+fs+"\": No such file or directory")
        return(1)
    
    p = list(bytearray(im.tobytes()))

    # Get payload size
    dl = ""
    td = 0
    l = 0
    for i in range(len(p)):
        td+=(p[i]&0b00000011)<<((3-i%4)*2)
        if(3-i%4==0):
            dl+=chr(td)
            if(td==0x00):
                try:
                    l = int(dl[:-1])
                except ValueError:
                    print(str(argv[0])+": Could not find hidden file size, likely there is no hidden file in this image.")
                    return(0)
                break
            td = 0

    # Get payload
    d = []
    td = 0
    for i in range(len(dl)*4,l*4+len(dl)*4):
        td+=(p[i]&0b00000011)<<((3-i%4)*2)
        if(3-i%4==0):
            d+=[td]
            td = 0
    print("Wrote file of size: "+str(l)+" bytes to: "+fs+".")

    f.write(bytes(d)) 
    f.close()
    return(0)

if(__name__ == "__main__"): # Garbage code for garbage people don't read fuck you
    if(len(argv)==4):
        if(argv[1]=="encode"):
            encode_image(argv[2],argv[3])
            exit()
        elif(argv[1]=="decode"):
            decode_image(argv[2],argv[3])
            exit()
    elif(len(argv)>1):
        if(argv[1]=="encode"):
            print(str(argv[0])+": Please include both an image file and a file to hide")
            print("\tUsage: "+str(argv[0])+" encode <image_to_encode> <file_to_hide>")
            exit()
        elif(argv[1]=="decode"):
            print(str(argv[0])+": Please include both an image file and a name for a new output file")
            print("\tUsage: "+str(argv[0])+" decode <image_to_decode> <output_file>")
            exit()
    print(str(argv[0])+": Incorrect arguments.")
    print("Usage:")
    print("\tEncoding: "+str(argv[0])+" encode <image_to_encode> <file_to_hide>")
    print("\tDecoding: "+str(argv[0])+" decode <image_to_decode> <output_file>")
