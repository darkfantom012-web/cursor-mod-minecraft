from PIL import Image
P = {
 '.':(0,0,0,0),
 'o':(26,20,16,255),    # outline
 'b':(92,58,33,255),    # boot dark
 'B':(140,92,52,255),   # boot mid
 'l':(186,132,76,255),  # boot light
 's':(118,196,255,255), # speed line
 'S':(200,240,255,255),
 'g':(60,60,66,255),    # sole
}
art = [
 "................",
 ".........oooo...",
 ".s......obBBllo.",
 "SSs.....oBBBBlo.",
 ".s......oBBBBlo.",
 "........oBBBBlo.",
 "..sS....oBBBBlo.",
 "sSSs....oBBBBlo.",
 "........oBBBBlo.",
 "..sS....oBBBBlo.",
 "sSS.....oBBBBlo.",
 "....ooooobBBBlo.",
 "...obBBBBBBBBlo.",
 "...olllllllllllo",
 "...oggggggggggo.",
 "....oooooooooo..",
]
img = Image.new("RGBA",(16,16))
for y,row in enumerate(art):
    for x,c in enumerate(row):
        img.putpixel((x,y),P[c])
import sys
img.save(sys.argv[1])
img.resize((128,128), Image.NEAREST).save(sys.argv[2])
