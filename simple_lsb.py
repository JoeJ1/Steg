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
        data = list(bytearray(f.read()))
        f.close()
    except FileNotFoundError:
        print(str(argv[0])+": \""+fs+"\": No such file or directory")

    w, h = im.size
    pix = list(bytearray(im.tobytes()))
    
    fulldata = [] # The data once it's been split into 2 bit chunks
    datalen=len(data) # It's nice to know the length of the data before the indicator is prepended
    data = [ord(i) for i in str(len(data))]+[0x00]+data # Prepend length of data (stored in ascii for some reason)
    for i in data:
        fulldata+=[i>>0b110-j*0b10 &0b11 for j in range(0b100)] # Terribly written bitshifting garbage to place the payload in the 2 LSBs of the image

    if(len(fulldata)>len(pix)):
        print(str(argv[0])+": data is too large to encode into image, get a bigger image or smaller data plz")
        return(1)

    for i in range(len(fulldata)):
        pix[i]=(pix[i]&0b11111100)+fulldata[i]

    pix = bytes(pix)
    nim = Image.frombytes("RGB", (w, h), pix)
    nim.save("new_"+ims)

    print("Encoded file of length "+str(datalen)+" bytes to new_"+ims)

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
    
    pix = list(bytearray(im.tobytes()))

    # Get data size
    datalen = ""
    thisbyte = 0
    length = 0
    for i in range(len(pix)):
        thisbyte+=(pix[i]&0b00000011)<<((3-i%4)*2) # Build current byte from LSBs
        if(3-i%4==0):
            datalen+=chr(thisbyte)
            if(thisbyte==0x00):
                try:
                    length = int(datalen[:-1]) # [:-1] used as length indicator is ended by null byte, this must be stripped before conversion
                except ValueError:
                    print(str(argv[0])+": Could not find hidden file size, likely there is no hidden file in this image.")
                    return(0)
                break
            thisbyte = 0

    # Get data
    data = []
    thisbyte = 0
    for i in range(len(datalen)*4,length*4+len(datalen)*4):
        thisbyte+=(pix[i]&0b00000011)<<((3-i%4)*2) # Build current byte from LSBs
        if(3-i%4==0):
            data+=[thisbyte]
            thisbyte = 0
    print("Wrote file of size: "+str(length)+" bytes to: "+fs+".")

    f.write(bytes(data)) 
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
