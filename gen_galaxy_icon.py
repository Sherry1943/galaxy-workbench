"""生成银河工作台图标 - 参考汪苏泷星糖小怪物太空风格"""
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

def make_galaxy_icon(size=180):
    pixels = bytearray(size * size * 4)
    cx, cy = size/2, size/2
    
    # 1. 银河深空背景
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            dx = x - cx
            dy = y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            
            # 圆角矩形
            radius = size * 0.22
            corner_check = max(abs(dx) - (size/2 - radius), 0) ** 2 + max(abs(dy) - (size/2 - radius), 0) ** 2
            if corner_check > radius * radius:
                pixels[idx:idx+4] = [0,0,0,0]
                continue
            
            # 银河渐变: 深紫蓝 → 浅紫粉
            t = dist / (size * 0.7)
            t = min(t, 1.0)
            
            if t < 0.3:
                # 中心: 亮粉紫
                r = int(180 + (1-t/0.3) * 40)
                g = int(120 + (1-t/0.3) * 40)
                b = int(200 + (1-t/0.3) * 30)
            elif t < 0.6:
                # 中间: 紫罗兰
                r2 = (t - 0.3) / 0.3
                r = int(220 - r2 * 100)
                g = int(160 - r2 * 80)
                b = int(230 - r2 * 50)
            else:
                # 边缘: 深紫蓝
                r2 = (t - 0.6) / 0.4
                r = int(120 - r2 * 80)
                g = int(80 - r2 * 50)
                b = int(180 - r2 * 100)
            
            # 添加星星
            star_seed = (int(x * 7.3 + y * 13.7) % 100)
            if star_seed < 5 and dist < size * 0.48:
                brightness = 200 + (star_seed * 15) % 55
                r = min(255, r + brightness)
                g = min(255, g + brightness)
                b = min(255, b + brightness)
            
            # 旋臂星云
            angle = math.atan2(dy, dx)
            spiral = (angle * 1.5 + dist * 0.07) % (math.pi * 2)
            spiral_factor = math.sin(spiral) * 0.5 + 0.5
            if dist < size * 0.35 and spiral_factor > 0.6:
                glow = int(spiral_factor * 40)
                r = min(255, r + glow)
                g = min(255, g + glow // 2)
                b = min(255, b + glow)
            
            pixels[idx:idx+4] = [r, g, b, 255]
    
    # 2. 画小怪物（粉猪+太空服）- 居中
    mc_x = size // 2
    mc_y = int(size * 0.55)
    
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            if pixels[idx + 3] == 0:
                continue
            
            dx = x - mc_x
            dy = y - mc_y
            
            # 太空服身体 (白色圆胖形)
            body_r = int(size * 0.22)
            if abs(dx) <= body_r and abs(dy) <= body_r * 0.95:
                ellipse = (dx*dx)/(body_r*body_r) + (dy*dy)/(body_r*0.95*body_r*0.95)
                if ellipse <= 1:
                    # 白色太空服
                    shadow = ellipse ** 0.5  # 边缘阴影
                    r = int(255 - shadow * 30)
                    g = int(255 - shadow * 30)
                    b = int(255 - shadow * 30)
                    pixels[idx:idx+4] = [r, g, b, 255]
                    
                    # 太空服边缘描边（浅灰）
                    if ellipse > 0.85:
                        pixels[idx:idx+4] = [220, 220, 230, 255]
            
            # 粉色脸蛋 (在身体前方)
            face_r = int(size * 0.13)
            fc_y = mc_y - int(size * 0.04)
            if abs(dx) <= face_r and abs(dy - (fc_y - mc_y)) <= face_r * 0.85:
                ellipse_f = (dx*dx)/(face_r*face_r) + ((dy - (fc_y - mc_y))**2)/(face_r*0.85*face_r*0.85)
                if ellipse_f <= 1:
                    # 粉红色
                    pixels[idx:idx+4] = [255, 130, 170, 255]
                    # 高光
                    if dy - (fc_y - mc_y) < -face_r*0.3 and dx < 0:
                        pixels[idx:idx+4] = [255, 180, 210, 255]
            
            # 触角 - 头顶两个小球（参考图片中的兔耳形状）
            for ax_off in [-int(size*0.07), int(size*0.07)]:
                ay = mc_y - body_r - int(size * 0.06)
                ax = mc_x + ax_off
                adx = x - ax
                ady = y - ay
                adist = (adx*adx + ady*ady) ** 0.5
                if adist < size * 0.035:
                    pixels[idx:idx+4] = [255, 100, 150, 255]
                # 高光
                if adist < size * 0.015 and adx < 0 and ady < 0:
                    pixels[idx:idx+4] = [255, 200, 220, 255]
                # 连接杆
                if abs(adx) < 2 and 0 < ady < size*0.06:
                    pixels[idx:idx+4] = [255, 150, 180, 255]
            
            # 眼睛（两点）
            eye_y = fc_y - int(size*0.01)
            eye_r = int(size * 0.012)
            for ex_off in [-int(size*0.04), int(size*0.04)]:
                edx = x - (mc_x + ex_off)
                edy = y - eye_y
                edist = (edx*edx + edy*edy) ** 0.5
                if edist < eye_r:
                    pixels[idx:idx+4] = [40, 30, 50, 255]
            
            # 微笑嘴巴
            mouth_y = mc_y + int(size * 0.02)
            mouth_dx = dx
            mouth_dy = y - mouth_y
            if abs(mouth_dx) < int(size*0.04) and abs(mouth_dy) < 2:
                # 检测在脸内部
                face_check_dx = dx
                face_check_dy = mouth_dy + int(size*0.04)
                if face_check_dx*face_check_dx + face_check_dy*face_check_dy < (size*0.13)**2:
                    pixels[idx:idx+4] = [180, 80, 110, 255]
            
            # 腮红
            for cx_off in [-int(size*0.075), int(size*0.075)]:
                bx = mc_x + cx_off
                bdx = x - bx
                bdy = y - (fc_y + int(size*0.015))
                bdist = (bdx*bdx + bdy*bdy) ** 0.5
                if bdist < size * 0.022:
                    pixels[idx:idx+4] = [255, 140, 170, 255]
    
    return bytes(pixels)

print("生成银河工作台图标...")
pixels = make_galaxy_icon(180)
png = make_png(180, 180, pixels)
with open('/workspace/apple-touch-icon.png', 'wb') as f:
    f.write(png)
print(f"图标: {len(png)} bytes")

# 小尺寸
pixels2 = make_galaxy_icon(120)
png2 = make_png(120, 120, pixels2)
with open('/workspace/icon-120.png', 'wb') as f:
    f.write(png2)
print(f"小图标: {len(png2)} bytes")
print("完成!")
