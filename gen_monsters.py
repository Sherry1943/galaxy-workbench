"""生成小怪物家族头像 - 参考汪苏泷周边风格"""
import struct, zlib, math

def make_png(width, height, pixels):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            idx = (y * width + x) * 4
            raw += bytes(pixels[idx:idx+4])
    idat = zlib.compress(raw)
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

def circle_check(x, y, cx, cy, r):
    return (x-cx)**2 + (y-cy)**2 < r*r

def draw_circle(pixels, size, cx, cy, r, color, alpha=255):
    for y in range(size):
        for x in range(size):
            idx = (y*size+x)*4
            if pixels[idx+3] == 0 and alpha > 0:
                continue
            if circle_check(x, y, cx, cy, r):
                pixels[idx:idx+4] = list(color) + [alpha]

def make_monster(size, body_color, eye_style='big', mouth_style='wide', has_ears=False, ear_color=None):
    """生成一个小怪物头像
    body_color: 身体颜色 (R,G,B)
    eye_style: 'big' 大眼睛, 'small' 小眼睛
    mouth_style: 'wide' 大嘴, 'smile' 微笑
    has_ears: 是否有耳朵/触角
    """
    pixels = bytearray(size * size * 4)
    cx, cy = size//2, size//2
    body_r = int(size * 0.38)
    
    # 圆角矩形背景（透明）
    for y in range(size):
        for x in range(size):
            idx = (y*size+x)*4
            dx = x - cx
            dy = y - cy
            radius = size * 0.22
            corner = max(abs(dx)-(size/2-radius),0)**2 + max(abs(dy)-(size/2-radius),0)**2
            if corner > radius*radius:
                continue  # 透明
            pixels[idx:idx+4] = [255, 255, 255, 0]
    
    # 耳朵/触角
    if has_ears and ear_color:
        ear_r = int(size * 0.1)
        for ex in [-int(size*0.2), int(size*0.2)]:
            ey = cy - body_r - int(size*0.05)
            draw_circle(pixels, size, cx+ex, ey, ear_r, ear_color)
    
    # 身体（圆形）
    for y in range(size):
        for x in range(size):
            idx = (y*size+x)*4
            if pixels[idx+3] == 0:
                continue
            dx = x - cx
            dy = y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < body_r:
                # 渐变身体色
                t = dist / body_r
                r = max(0, min(255, int(body_color[0] * (1 - t*0.15) + 20*t)))
                g = max(0, min(255, int(body_color[1] * (1 - t*0.15) + 10*t)))
                b = max(0, min(255, int(body_color[2] * (1 - t*0.15) + 10*t)))
                pixels[idx:idx+4] = [r, g, b, 255]
                # 高光
                if dy < -body_r*0.3 and dx < -body_r*0.2:
                    hl = int(40 * (1 - abs(dy/(body_r*0.5))))
                    pixels[idx] = min(255, pixels[idx]+hl)
                    pixels[idx+1] = min(255, pixels[idx+1]+hl)
                    pixels[idx+2] = min(255, pixels[idx+2]+hl)
    
    # 眼睛
    eye_r = int(size * 0.06) if eye_style == 'big' else int(size * 0.04)
    eye_offset = int(size * 0.1)
    eye_y = cy - int(size * 0.05)
    
    for ex in [-eye_offset, eye_offset]:
        ecx = cx + ex
        # 眼白
        draw_circle(pixels, size, ecx, eye_y, eye_r, [255, 255, 255])
        # 瞳孔
        pupil_r = eye_r * 0.55
        draw_circle(pixels, size, ecx, eye_y, int(pupil_r), [40, 30, 50])
        # 高光
        draw_circle(pixels, size, ecx-2, eye_y-2, max(1, int(pupil_r*0.4)), [255, 255, 255])
    
    # 嘴巴
    mouth_y = cy + int(size * 0.1)
    mouth_w = int(size * 0.12)
    
    if mouth_style == 'wide':
        # 大嘴 - 椭圆
        for y in range(size):
            for x in range(size):
                idx = (y*size+x)*4
                if pixels[idx+3] == 0:
                    continue
                dx = x - cx
                dy = y - mouth_y
                # 椭圆嘴巴
                if (dx*dx)/(mouth_w*mouth_w) + (dy*dy)/((mouth_w*0.5)*(mouth_w*0.5)) < 1:
                    pixels[idx:idx+4] = [80, 30, 50, 255]
                    # 牙齿（白色小方块）
                    if dy < -mouth_w*0.2 and abs(dx) < mouth_w*0.3:
                        pixels[idx:idx+4] = [255, 255, 255, 255]
    else:
        # 微笑
        for y in range(size):
            for x in range(size):
                idx = (y*size+x)*4
                if pixels[idx+3] == 0:
                    continue
                dx = x - cx
                dy = y - mouth_y
                if abs(dx) < mouth_w and dy >= 0 and dy <= 4:
                    curve = math.cos((dx/mouth_w)*math.pi/2)*3
                    if abs(dy - curve) < 1.5:
                        pixels[idx:idx+4] = [100, 40, 60, 255]
    
    # 腮红
    blush_r = int(size * 0.04)
    for bx in [-int(size*0.18), int(size*0.18)]:
        draw_circle(pixels, size, cx+bx, cy+int(size*0.05), blush_r, [255, 150, 170, 200])
    
    return bytes(pixels)

# 生成5个小怪物 + 1个主图标
monsters = [
    # (文件名, 身体色, 眼睛, 嘴巴, 耳朵, 耳朵色)
    ('monster1.png', (255, 130, 170), 'big', 'wide', True, (255, 100, 150)),   # 粉色大嘴+耳朵
    ('monster2.png', (200, 130, 255), 'big', 'smile', True, (180, 110, 240)),   # 紫色微笑+耳朵
    ('monster3.png', (255, 160, 100), 'small', 'wide', False, None),             # 橙色大嘴
    ('monster4.png', (255, 210, 100), 'big', 'smile', False, None),              # 黄色微笑
    ('monster5.png', (130, 200, 255), 'small', 'smile', True, (100, 180, 240)), # 蓝色+耳朵
]

for name, color, eyes, mouth, ears, ear_c in monsters:
    pixels = make_monster(120, color, eyes, mouth, ears, ear_c)
    png = make_png(120, 120, pixels)
    with open(f'/workspace/{name}', 'wb') as f:
        f.write(png)
    print(f"✅ {name} ({len(png)} bytes)")

# 主图标 - 粉色大嘴怪物 + 银河背景
def make_galaxy_monster_icon(size=180):
    pixels = bytearray(size * size * 4)
    cx, cy = size/2, size/2
    
    # 银河背景
    for y in range(size):
        for x in range(size):
            idx = (y*size+x)*4
            dx, dy = x-cx, y-cy
            dist = (dx*dx+dy*dy)**0.5
            radius = size * 0.22
            corner = max(abs(dx)-(size/2-radius),0)**2 + max(abs(dy)-(size/2-radius),0)**2
            if corner > radius*radius:
                pixels[idx:idx+4] = [0,0,0,0]
                continue
            t = min(dist/(size*0.7), 1.0)
            if t < 0.3:
                r = int(180+(1-t/0.3)*40); g = int(120+(1-t/0.3)*40); b = int(200+(1-t/0.3)*30)
            elif t < 0.6:
                r2 = (t-0.3)/0.3; r = int(220-r2*100); g = int(160-r2*80); b = int(230-r2*50)
            else:
                r2 = (t-0.6)/0.4; r = int(120-r2*80); g = int(80-r2*50); b = int(180-r2*100)
            # 星星
            if (int(x*7.3+y*13.7)%100) < 5 and dist < size*0.48:
                br = 200+(int(x*7.3+y*13.7)*15)%55
                r = min(255,r+br); g = min(255,g+br); b = min(255,b+br)
            pixels[idx:idx+4] = [r,g,b,255]
    
    # 小怪物（粉色，大嘴，有耳朵）
    mc_x, mc_y = size//2, int(size*0.52)
    body_r = int(size*0.2)
    body_color = (255, 130, 170)
    
    # 耳朵
    ear_r = int(size*0.05)
    for ex in [-int(size*0.1), int(size*0.1)]:
        ey = mc_y - body_r - int(size*0.03)
        draw_circle(pixels, size, mc_x+ex, ey, ear_r, (255, 100, 150))
    
    # 身体
    for y in range(size):
        for x in range(size):
            idx = (y*size+x)*4
            if pixels[idx+3] == 0:
                continue
            dx, dy = x-mc_x, y-mc_y
            dist = (dx*dx+dy*dy)**0.5
            if dist < body_r:
                t = dist/body_r
                r = min(255, int(body_color[0]*(1-t*0.1)+15))
                g = min(255, int(body_color[1]*(1-t*0.1)+10))
                b = min(255, int(body_color[2]*(1-t*0.1)+10))
                pixels[idx:idx+4] = [r,g,b,255]
                if dy < -body_r*0.3 and dx < -body_r*0.2:
                    hl = int(40*(1-abs(dy/(body_r*0.5))))
                    pixels[idx] = min(255,pixels[idx]+hl)
                    pixels[idx+1] = min(255,pixels[idx+1]+hl)
                    pixels[idx+2] = min(255,pixels[idx+2]+hl)
    
    # 眼睛
    eye_r = int(size*0.035)
    eye_off = int(size*0.055)
    eye_y = mc_y - int(size*0.03)
    for ex in [-eye_off, eye_off]:
        draw_circle(pixels, size, mc_x+ex, eye_y, eye_r, [255,255,255])
        draw_circle(pixels, size, mc_x+ex, eye_y, int(eye_r*0.55), [40,30,50])
        draw_circle(pixels, size, mc_x+ex-1, eye_y-1, max(1,int(eye_r*0.3)), [255,255,255])
    
    # 大嘴
    mouth_y = mc_y + int(size*0.06)
    mouth_w = int(size*0.07)
    for y in range(size):
        for x in range(size):
            idx = (y*size+x)*4
            if pixels[idx+3] == 0:
                continue
            dx, dy = x-mc_x, y-mouth_y
            if (dx*dx)/(mouth_w*mouth_w) + (dy*dy)/((mouth_w*0.5)*(mouth_w*0.5)) < 1:
                pixels[idx:idx+4] = [80,30,50,255]
                if dy < -mouth_w*0.2 and abs(dx) < mouth_w*0.3:
                    pixels[idx:idx+4] = [255,255,255,255]
    
    # 腮红
    draw_circle(pixels, size, mc_x-int(size*0.09), mc_y+int(size*0.02), int(size*0.025), [255,150,170,200])
    draw_circle(pixels, size, mc_x+int(size*0.09), mc_y+int(size*0.02), int(size*0.025), [255,150,170,200])
    
    return bytes(pixels)

pixels = make_galaxy_monster_icon(180)
png = make_png(180, 180, pixels)
with open('/workspace/apple-touch-icon.png', 'wb') as f:
    f.write(png)
print(f"✅ apple-touch-icon.png ({len(png)} bytes)")

print("全部完成!")
