"""生成小怪物头像 - 修复版"""
import struct, zlib, math

def make_png(w, h, pixels):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    raw = b''
    for y in range(h):
        raw += b'\x00'
        for x in range(w):
            idx = (y*w+x)*4
            raw += bytes(pixels[idx:idx+4])
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')

def make_monster(size, body_color, eye_style='big', mouth_style='wide', has_ears=False, ear_color=None):
    pixels = bytearray(size * size * 4)
    cx, cy = size//2, size//2
    body_r = int(size * 0.35)
    
    # 1. 先全部设为透明
    for i in range(size*size):
        pixels[i*4+3] = 0
    
    # 2. 圆角矩形背景区域设为透明（已经是了）
    # 3. 画耳朵（在身体后面）
    if has_ears and ear_color:
        ear_r = int(size * 0.12)
        for ex in [-int(size*0.22), int(size*0.22)]:
            ey = cy - body_r - int(size*0.02)
            for y in range(max(0,ey-ear_r), min(size, ey+ear_r)):
                for x in range(max(0,cx+ex-ear_r), min(size, cx+ex+ear_r)):
                    if (x-(cx+ex))**2 + (y-ey)**2 < ear_r**2:
                        idx = (y*size+x)*4
                        pixels[idx:idx+4] = list(ear_color) + [255]
    
    # 4. 画身体（圆形）
    for y in range(size):
        for x in range(size):
            dx, dy = x-cx, y-cy
            dist = (dx*dx+dy*dy)**0.5
            if dist < body_r:
                idx = (y*size+x)*4
                t = dist / body_r
                r = max(0, min(255, int(body_color[0]*(1-t*0.12)+18*t)))
                g = max(0, min(255, int(body_color[1]*(1-t*0.12)+12*t)))
                b = max(0, min(255, int(body_color[2]*(1-t*0.12)+12*t)))
                pixels[idx:idx+4] = [r, g, b, 255]
                # 高光
                if dy < -body_r*0.3 and dx < -body_r*0.2:
                    hl = int(45 * (1 - abs(dy/(body_r*0.5))))
                    pixels[idx] = min(255, pixels[idx]+hl)
                    pixels[idx+1] = min(255, pixels[idx+1]+hl)
                    pixels[idx+2] = min(255, pixels[idx+2]+hl)
    
    # 5. 眼睛
    eye_r = int(size*0.06) if eye_style=='big' else int(size*0.04)
    eye_off = int(size*0.1)
    eye_y = cy - int(size*0.05)
    for ex in [-eye_off, eye_off]:
        ecx = cx + ex
        # 眼白
        for y in range(max(0,eye_y-eye_r), min(size,eye_y+eye_r)):
            for x in range(max(0,ecx-eye_r), min(size,ecx+eye_r)):
                if (x-ecx)**2+(y-eye_y)**2 < eye_r**2:
                    idx = (y*size+x)*4
                    pixels[idx:idx+4] = [255,255,255,255]
        # 瞳孔
        pr = int(eye_r*0.55)
        for y in range(max(0,eye_y-pr), min(size,eye_y+pr)):
            for x in range(max(0,ecx-pr), min(size,ecx+pr)):
                if (x-ecx)**2+(y-eye_y)**2 < pr**2:
                    idx = (y*size+x)*4
                    pixels[idx:idx+4] = [40,30,50,255]
        # 高光
        hr = max(1, int(pr*0.4))
        for y in range(max(0,eye_y-1-hr), min(size,eye_y-1+hr)):
            for x in range(max(0,ecx-2-hr), min(size,ecx-2+hr)):
                if (x-(ecx-2))**2+(y-(eye_y-2))**2 < hr**2:
                    idx = (y*size+x)*4
                    pixels[idx:idx+4] = [255,255,255,255]
    
    # 6. 嘴巴
    mouth_y = cy + int(size*0.1)
    mouth_w = int(size*0.13)
    if mouth_style == 'wide':
        for y in range(max(0,mouth_y-int(mouth_w*0.5)), min(size,mouth_y+int(mouth_w*0.5))):
            for x in range(max(0,cx-mouth_w), min(size,cx+mouth_w)):
                dx, dy = x-cx, y-mouth_y
                if (dx*dx)/(mouth_w*mouth_w) + (dy*dy)/((mouth_w*0.5)*(mouth_w*0.5)) < 1:
                    idx = (y*size+x)*4
                    pixels[idx:idx+4] = [80,30,50,255]
                    # 牙齿
                    if dy < -mouth_w*0.15 and abs(dx) < mouth_w*0.35:
                        pixels[idx:idx+4] = [255,255,255,255]
    else:
        for y in range(max(0,mouth_y), min(size,mouth_y+5)):
            for x in range(max(0,cx-mouth_w), min(size,cx+mouth_w)):
                dx, dy = x-cx, y-mouth_y
                curve = math.cos((dx/mouth_w)*math.pi/2)*3
                if abs(dy - curve) < 1.5:
                    idx = (y*size+x)*4
                    pixels[idx:idx+4] = [100,40,60,255]
    
    # 7. 腮红
    blush_r = int(size*0.045)
    for bx in [-int(size*0.18), int(size*0.18)]:
        for y in range(max(0,cy+int(size*0.05)-blush_r), min(size,cy+int(size*0.05)+blush_r)):
            for x in range(max(0,cx+bx-blush_r), min(size,cx+bx+blush_r)):
                if (x-(cx+bx))**2+(y-(cy+int(size*0.05)))**2 < blush_r**2:
                    idx = (y*size+x)*4
                    if pixels[idx+3] > 0:  # 只在身体上画
                        pixels[idx:idx+4] = [255,150,170,255]
    
    return bytes(pixels)

# 5个小怪物
monsters = [
    ('monster1.png', (255,130,170), 'big', 'wide', True, (255,100,150)),   # 粉色大嘴
    ('monster2.png', (200,130,255), 'big', 'smile', True, (180,110,240)),  # 紫色微笑
    ('monster3.png', (255,160,100), 'small', 'wide', False, None),          # 橙色大嘴
    ('monster4.png', (255,210,100), 'big', 'smile', False, None),           # 黄色微笑
    ('monster5.png', (130,200,255), 'small', 'smile', True, (100,180,240)),# 蓝色
]

for name, color, eyes, mouth, ears, ear_c in monsters:
    px = make_monster(120, color, eyes, mouth, ears, ear_c)
    png = make_png(120, 120, px)
    with open(f'/workspace/{name}', 'wb') as f:
        f.write(png)
    print(f"✅ {name} ({len(png)} bytes)")

print("完成!")
