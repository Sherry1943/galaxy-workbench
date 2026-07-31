"""生成粉色小怪物主题PNG图标 - 参考汪苏泷周边风格"""
import struct, zlib, math, random

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

def make_pink_monster_icon(size=180):
    random.seed(42)
    pixels = bytearray(size * size * 4)
    
    cx, cy = size/2, size/2
    
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            dx = x - cx
            dy = y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            
            # 圆角矩形裁剪
            radius = size * 0.22
            corner_check = max(abs(dx) - (size/2 - radius), 0) ** 2 + max(abs(dy) - (size/2 - radius), 0) ** 2
            if corner_check > radius * radius:
                pixels[idx:idx+4] = [0,0,0,0]
                continue
            
            # 粉色渐变背景: 浅粉 -> 蜜桃粉
            t_y = (y / size)
            r = int(255)
            g = int(220 + (0.5 - t_y) * 30)
            b = int(230 + (0.5 - t_y) * 20)
            
            # 右上角柔光
            rdx = x - size*0.7
            rdy = y - size*0.3
            rdist = (rdx*rdx + rdy*rdy) ** 0.5
            if rdist < size*0.3:
                glow = (1 - rdist/(size*0.3)) * 0.3
                r = min(255, int(r + glow*20))
                g = min(255, int(g + glow*30))
                b = min(255, int(b + glow*10))
            
            pixels[idx:idx+4] = [r, g, b, 255]
    
    # 画小怪物 - 圆胖形
    monster_cx = size // 2
    monster_cy = int(size * 0.52)
    monster_r = int(size * 0.20)
    
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            if pixels[idx + 3] == 0:
                continue
            
            dx = x - monster_cx
            dy = y - monster_cy
            dist_m = (dx*dx + dy*dy) ** 0.5
            
            # 怪物身体 - 椭圆形 (胖一些)
            if dist_m < monster_r * 1.1:
                # 主色: 粉红
                body_t = dist_m / (monster_r * 1.1)
                br = int(255)
                bg = int(160 - body_t * 30)
                bb = int(180 - body_t * 20)
                pixels[idx:idx+4] = [br, bg, bb, 255]
                
                # 身体高光 (左上)
                if dy < 0 and dx < 0:
                    hl = int(50 * (1 - dist_m / (monster_r * 0.8)))
                    pixels[idx] = min(255, pixels[idx] + hl)
                    pixels[idx+1] = min(255, pixels[idx+1] + hl // 2)
                    pixels[idx+2] = min(255, pixels[idx+2] + hl // 2)
            
            # 触角 - 头顶两根天线带小球
            antenna_offset = int(size * 0.07)
            for ax in [-antenna_offset, antenna_offset]:
                # 杆
                ant_top_y = monster_cy - int(monster_r * 0.9) - int(size * 0.08)
                ant_bot_y = monster_cy - int(monster_r * 0.6)
                if ant_bot_y <= y <= ant_top_y:
                    if abs(x - (monster_cx + ax)) < 2:
                        pixels[idx:idx+4] = [255, 130, 170, 255]
                # 顶部小球
                ball_y = ant_top_y - int(size * 0.015)
                ball_dx = x - (monster_cx + ax)
                ball_dy = y - ball_y
                if (ball_dx*ball_dx + ball_dy*ball_dy) ** 0.5 < size * 0.025:
                    pixels[idx:idx+4] = [255, 90, 150, 255]
                    # 高光
                    if ball_dx < -2 and ball_dy < -2:
                        if (ball_dx*ball_dx + ball_dy*ball_dy) ** 0.5 < size * 0.012:
                            pixels[idx:idx+4] = [255, 200, 220, 255]
            
            # 大眼睛 - 圆形
            eye_y = monster_cy - int(size * 0.025)
            eye_r = int(size * 0.045)
            eye_offset = int(size * 0.055)
            for ex in [-eye_offset, eye_offset]:
                ecx = monster_cx + ex
                edx = x - ecx
                edy = y - eye_y
                edist = (edx*edx + edy*edy) ** 0.5
                if edist < eye_r:
                    # 眼白
                    pixels[idx:idx+4] = [255, 255, 255, 255]
                    # 黑瞳孔
                    pupil_r = eye_r * 0.55
                    if edist < pupil_r:
                        pixels[idx:idx+4] = [40, 30, 50, 255]
                    # 高光
                    if edx < -1 and edy < -1 and edist < eye_r * 0.4:
                        pixels[idx:idx+4] = [255, 255, 255, 255]
                    # 第二小高光
                    if edx > 2 and edy > 2 and edist < eye_r * 0.4:
                        pixels[idx:idx+4] = [255, 230, 240, 255]
            
            # 嘴巴 - 微笑 (W形/小曲线)
            mouth_cy = monster_cy + int(size * 0.05)
            mouth_w = int(size * 0.05)
            mouth_dx = dx
            mouth_dy = y - mouth_cy
            # 微笑弧线
            if abs(mouth_dx) < mouth_w and mouth_dy >= 0 and mouth_dy <= 4:
                # 中间弧形
                curve = math.cos((mouth_dx / mouth_w) * math.pi / 2) * 3
                if abs(mouth_dy - curve) < 1.5:
                    pixels[idx:idx+4] = [180, 80, 110, 255]
            # 小腮红
            for cx_off in [-int(size*0.08), int(size*0.08)]:
                bx = monster_cx + cx_off
                bdx = x - bx
                bdy = y - (monster_cy + int(size*0.02))
                bdist = (bdx*bdx + bdy*bdy) ** 0.5
                if bdist < size * 0.025:
                    pixels[idx:idx+4] = [255, 140, 160, 255]
    
    return bytes(pixels)

print("生成粉色小怪物图标...")
pixels = make_pink_monster_icon(180)
png_data = make_png(180, 180, pixels)
with open('/workspace/apple-touch-icon.png', 'wb') as f:
    f.write(png_data)
print(f"图标已生成: {len(png_data)} bytes")

# 再生成小尺寸(用于favicon等)
pixels2 = make_pink_monster_icon(120)
png_data2 = make_png(120, 120, pixels2)
with open('/workspace/icon-120.png', 'wb') as f:
    f.write(png_data2)
print(f"小图标已生成: {len(png_data2)} bytes")
print("完成!")
