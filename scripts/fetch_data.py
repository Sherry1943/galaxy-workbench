#!/usr/bin/env python3
"""抓取财经数据并写入JSON文件"""
import json, urllib.request, re, os, time
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
    'Referer': 'https://finance.sina.com.cn'
}

def fetch_url(url, encoding='gbk'):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode(encoding, errors='replace')
    except Exception as e:
        print(f"  请求失败 {url}: {e}")
        return ''

def parse_sina_quote(raw, prefix='s_'):
    """解析新浪简式行情 s_sh000001="上证指数,3804.69,-23.78,-0.62,5922989,110647727" """
    results = {}
    for line in raw.strip().split('\n'):
        line = line.strip()
        if not line or '=' not in line:
            continue
        m = re.search(r'var hq_str_s_\w+="(.+)"', line)
        if not m:
            continue
        code_m = re.search(r'var hq_str_(s_\w+)=', line)
        code = code_m.group(1) if code_m else ''
        parts = m.group(1).split(',')
        if len(parts) >= 5:
            results[code] = {
                'name': parts[0],
                'price': float(parts[1]),
                'change': float(parts[2]),
                'change_pct': float(parts[3]),
                'volume': int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0,
                'amount': int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0,
            }
    return results

def fetch_market():
    """抓取四大指数"""
    print("📊 抓取指数行情...")
    raw = fetch_url('https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006,s_sh000688')
    data = parse_sina_quote(raw)
    
    index_map = {
        's_sh000001': {'key': 'sh', 'name': '上证指数'},
        's_sz399001': {'key': 'sz', 'name': '深证成指'},
        's_sz399006': {'key': 'cyb', 'name': '创业板指'},
        's_sh000688': {'key': 'kc50', 'name': '科创50'},
    }
    
    result = []
    for code, info in index_map.items():
        if code in data:
            d = data[code]
            result.append({
                'name': info['name'],
                'code': code.replace('s_', ''),
                'price': d['price'],
                'change': d['change'],
                'change_pct': d['change_pct'],
                'direction': 'up' if d['change'] >= 0 else 'down',
            })
    
    output = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'data': result}
    with open(os.path.join(DATA_DIR, 'market.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 指数: {len(result)}条")
    return output

def fetch_stocks():
    """抓取热门个股"""
    print("📈 抓取热门个股...")
    codes = 's_sh600519,s_sz300750,s_sh601318,s_sz300308,s_sz001309,s_sh600000'
    raw = fetch_url(f'https://hq.sinajs.cn/list={codes}')
    data = parse_sina_quote(raw)
    
    result = []
    for code, d in data.items():
        result.append({
            'name': d['name'],
            'code': code.replace('s_', ''),
            'price': d['price'],
            'change_pct': d['change_pct'],
            'direction': 'up' if d['change'] >= 0 else 'down',
        })
    
    output = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'data': result}
    with open(os.path.join(DATA_DIR, 'stocks.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 个股: {len(result)}条")
    return output

def fetch_news():
    """抓取财经新闻"""
    print("📰 抓取财经新闻...")
    result = []
    
    # 东方财富搜索API (JSONP格式，需解析)
    try:
        import urllib.parse
        param = json.dumps({
            "uid": "", "keyword": "财经", "type": ["cmsArticleWebOld"],
            "client": "web", "clientType": "web", "clientVersion": "curr",
            "param": {"cmsArticleWebOld": {"searchScope": "default", "sort": "default", "pageIndex": 1, "pageSize": 10, "preTag": "", "postTag": ""}}
        })
        encoded = urllib.parse.quote(param)
        url = f'https://search-api-web.eastmoney.com/search/jsonp?cb=jQuery&param={encoded}'
        raw = fetch_url(url, encoding='utf-8')
        if raw and raw.startswith('jQuery('):
            json_str = raw[7:-1]  # 去掉 jQuery() 包装
            j = json.loads(json_str)
            items = j.get('result', {}).get('cmsArticleWebOld', [])
            for item in items[:10]:
                title = item.get('title', '').replace('<em>', '').replace('</em>', '')
                digest = item.get('content', '')[:200].replace('<em>', '').replace('</em>', '') if item.get('content') else title
                result.append({
                    'title': title,
                    'digest': digest,
                    'source': item.get('mediaName', ''),
                    'time': item.get('date', ''),
                    'url': item.get('url', ''),
                })
    except Exception as e:
        print(f"  东方财富新闻API失败: {e}")
    
    # 备用：新浪要闻
    if not result:
        try:
            raw = fetch_url('https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2510&num=10&page=1', encoding='utf-8')
            if raw:
                j = json.loads(raw)
                items = j.get('result', {}).get('data', [])
                for item in items[:10]:
                    title = item.get('title', '')
                    result.append({
                        'title': title,
                        'digest': item.get('intro', '')[:200] if item.get('intro') else title,
                        'source': '新浪财经',
                        'time': datetime.fromtimestamp(int(item.get('ctime', 0))).strftime('%m月%d日 %H:%M') if item.get('ctime') else '',
                        'url': item.get('url', ''),
                    })
        except Exception as e:
            print(f"  新浪新闻备用API失败: {e}")
    
    output = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'data': result}
    with open(os.path.join(DATA_DIR, 'news.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 新闻: {len(result)}条")
    return output

def fetch_bonds():
    """抓取可转债数据"""
    print("💎 抓取可转债数据...")
    result = []
    
    # 东方财富可转债API - 双低排序
    url = 'https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_BOND_CBLIST&columns=SECURITY_CODE,SECURITY_NAME_ABBR,NEW_PRICE,PREMIUM_RATIO,BOND_CODE,DOUBLE_LOW&pageSize=20&pageNumber=1&sortColumns=DOUBLE_LOW&sortTypes=1'
    raw = fetch_url(url, encoding='utf-8')
    
    try:
        j = json.loads(raw)
        rows = j.get('result', {}).get('data', [])
        if rows:
            for row in rows[:6]:
                result.append({
                    'name': row.get('SECURITY_NAME_ABBR', ''),
                    'code': str(row.get('BOND_CODE', '')),
                    'price': round(float(row.get('NEW_PRICE', 0)), 2),
                    'premium': round(float(row.get('PREMIUM_RATIO', 0)), 2),
                    'double_low': round(float(row.get('DOUBLE_LOW', 0)), 2),
                })
    except Exception as e:
        print(f"  东方财富可转债API失败: {e}")
    
    # 备用：静态数据（上次成功获取的）
    if not result:
        print("  使用缓存可转债数据")
        fallback = [
            {'name': '密卫转债', 'code': '113658', 'price': 109.73, 'premium': 0.66, 'double_low': 110.39},
            {'name': '美锦转债', 'code': '127061', 'price': 108.71, 'premium': 5.36, 'double_low': 114.07},
            {'name': '闻泰转债', 'code': '110081', 'price': 100.68, 'premium': 15.46, 'double_low': 116.14},
            {'name': '大参转债', 'code': '113605', 'price': 118.99, 'premium': 4.87, 'double_low': 123.86},
            {'name': '鸿路转债', 'code': '128134', 'price': 121.36, 'premium': 5.19, 'double_low': 126.55},
            {'name': '齐翔转2', 'code': '128128', 'price': 110.25, 'premium': 16.54, 'double_low': 126.79},
        ]
        result = fallback
    
    output = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'data': result}
    with open(os.path.join(DATA_DIR, 'bonds.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 可转债: {len(result)}条")
    return output

if __name__ == '__main__':
    print(f"=== 财经数据抓取 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        fetch_market()
    except Exception as e:
        print(f"指数抓取异常: {e}")
    try:
        fetch_stocks()
    except Exception as e:
        print(f"个股抓取异常: {e}")
    try:
        fetch_news()
    except Exception as e:
        print(f"新闻抓取异常: {e}")
    try:
        fetch_bonds()
    except Exception as e:
        print(f"可转债抓取异常: {e}")
    print("=== 抓取完成 ===")
