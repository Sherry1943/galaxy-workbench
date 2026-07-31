"""生成银河小怪物主题的PNG图标"""
import struct, zlib, os

def make_png(width, height, pixels):
    """从RGB像素数组生成PNG文件"""
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    # PNG signature
    sig = b'\x89PNG\r\n\x1a\n'
    # IHDR
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    # IDAT - raw pixel data with filter byte per row
    raw = b''
    for y in range(height):
        raw += b'\x00'  # filter: none
        for x in range(width):
            idx = (y * width + x) * 4
            raw += bytes(pixels[idx:idx+4])
    idat = zlib.compress(raw)
    # IEND
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

def galacy_monster_icon(size=180):
    """银河小怪物图标 - 深空背景+可爱小怪物"""
    pixels = bytearray(size * size * 4)
    
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            dx = x - size/2
            dy = y - size/2
            dist = (dx*dx + dy*dy) ** 0.5
            
            # 圆角矩形裁剪
            radius = size * 0.22
            # 四角圆角检测
            cx = max(abs(dx), abs(dy))
            corner_check = max(abs(dx) - (size/2 - radius), 0) ** 2 + max(abs(dy) - (size/2 - radius), 0) ** 2
            if corner_check > radius * radius:
                pixels[idx:idx+4] = [0,0,0,0]  # 透明
                continue
            
            # 银河渐变背景
            t = dist / (size * 0.7)
            t = min(t, 1.0)
            
            # 深空渐变: 中心亮紫 -> 外围深蓝黑
            if t < 0.3:
                r = int(80 + (1-t/0.3) * 60)
                g = int(30 + (1-t/0.3) * 20)
                b = int(120 + (1-t/0.3) * 80)
            elif t < 0.6:
                r2 = (t - 0.3) / 0.3
                r = int(140 - r2 * 80)
                g = int(50 - r2 * 30)
                b = int(200 - r2 * 80)
            else:
                r2 = (t - 0.6) / 0.4
                r = int(60 - r2 * 40)
                g = int(20 - r2 * 15)
                b = int(120 - r2 * 80)
            
            # 添加星星
            import math
            star_seed = int(x * 7.3 + y * 13.7) % 100
            if star_seed < 3 and dist < size * 0.45:
                brightness = 200 + (star_seed * 18) % 55
                r = min(255, r + brightness)
                g = min(255, g + brightness)
                b = min(255, b + brightness)
            
            # 星云效果 - 旋臂
            angle = math.atan2(dy, dx)
            spiral = (angle * 2 + dist * 0.08) % (math.pi * 2)
            spiral_factor = math.sin(spiral) * 0.5 + 0.5
            if dist < size * 0.35 and spiral_factor > 0.6:
                glow = int(spiral_factor * 30)
                r = min(255, r + glow)
                g = min(255, g + glow // 3)
                b = min(255, b + glow)
            
            pixels[idx:idx+4] = [r, g, b, 255]
    
    # 画小怪物 - 中心位置
    monster_cx = size // 2
    monster_cy = int(size * 0.52)
    monster_r = int(size * 0.18)  # 身体半径
    
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            if pixels[idx + 3] == 0:
                continue
            
            dx = x - monster_cx
            dy = y - monster_cy
            dist_m = (dx*dx + dy*dy) ** 0.5
            
            # 怪物身体 (圆角矩形/椭圆形)
            if dist_m < monster_r:
                # 渐变色身体: 粉紫 -> 蓝紫
                body_t = dist_m / monster_r
                br = int(180 - body_t * 40)
                bg = int(100 - body_t * 40)
                bb = int(220 - body_t * 20)
                pixels[idx:idx+4] = [br, bg, bb, 255]
                
                # 身体高光
                if dy < -monster_r * 0.3 and dx < 0:
                    hl = int(60 * (1 - abs(dy / (monster_r * 0.5))))
                    pixels[idx] = min(255, pixels[idx] + hl)
                    pixels[idx+1] = min(255, pixels[idx+1] + hl)
                    pixels[idx+2] = min(255, pixels[idx+2] + hl)
            
            # 怪物触角 (两个小球)
            antenna_y = monster_cy - monster_r - int(size * 0.04)
            for ax in [-int(size*0.06), int(size*0.06)]:
                adx = x - (monster_cx + ax)
                ady = y - antenna_y
                adist = (adx*adx + ady*ady) ** 0.5
                if adist < size * 0.025:
                    pixels[idx:idx+4] = [255, 150, 200, 255]  # 粉色触角尖
            
            # 眼睛 (两个大眼睛)
            eye_r = int(size * 0.035)
            eye_offset = int(size * 0.05)
            for ex in [-eye_offset, eye_offset]:
                edx = x - (monster_cx + ex)
                edy = y - (monster_cy - int(size*0.02))
                edist = (edx*edx + edy*edy) ** 0.5
                if edist < eye_r:
                    # 眼白
                    pixels[idx:idx+4] = [255, 255, 255, 255]
                    # 瞳孔
                    pupil_r = eye_r * 0.5
                    if edist < pupil_r:
                        pixels[idx:idx+4] = [40, 20, 80, 255]  # 深紫瞳孔
                    # 高光
                    if edx < -1 and edy < -1 and edist < eye_r * 0.7:
                        pixels[idx:idx+4] = [255, 255, 255, 255]
            
            # 嘴巴 (微笑曲线)
            mouth_cy = monster_cy + int(size * 0.06)
            mouth_dx = dx
            mouth_dy = dy - int(size * 0.06)
            mouth_dist = (mouth_dx*mouth_dx + mouth_dy*mouth_dy) ** 0.5
            mouth_w = int(size * 0.06)
            if abs(mouth_dy) < 2 and abs(mouth_dx) < mouth_w and mouth_dy > 0:
                pixels[idx:idx+4] = [60, 30, 80, 255]
    
    return bytes(pixels)

# 生成180x180图标
print("生成银河小怪物图标...")
pixels = galacy_monster_icon(180)
png_data = make_png(180, 180, pixels)

with open('/workspace/apple-touch-icon.png', 'wb') as f:
    f.write(png_data)

print(f"图标已生成: {len(png_data)} bytes")
print("完成!")
