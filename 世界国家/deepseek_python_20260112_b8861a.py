import re
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

def extract_countries_from_svg(file_path: str) -> List[Dict[str, str]]:
    """
    从 SVG 文件中提取所有国家的信息
    
    Args:
        file_path: SVG 文件路径
        
    Returns:
        包含所有国家信息的字典列表
    """
    countries = []
    
    try:
        # 解析 SVG 文件
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # 查找所有 path 元素
        # SVG 中可能有命名空间，需要处理
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        
        # 如果没有命名空间，直接查找
        paths = root.findall('.//path')
        if not paths:  # 如果没找到，尝试带命名空间查找
            paths = root.findall('.//svg:path', namespaces)
        
        for path in paths:
            country_info = {}
            
            # 获取各个属性
            country_info['id'] = path.get('id', '')
            
            # 获取 data-* 属性
            country_info['name_zh'] = path.get('data-name_zht', path.get('data-name_zh', ''))
            country_info['name_en'] = path.get('data-name_en', '')
            country_info['formal_en'] = path.get('data-formal_en', '')
            country_info['type'] = path.get('data-type', '')
            country_info['sovereignty'] = path.get('data-sovereignt', '')
            
            # 如果通过 data-name_zht 没找到，尝试从 id 获取中文名
            if not country_info['name_zh'] and country_info['id']:
                country_info['name_zh'] = country_info['id']
            
            # 只添加有有效信息的国家
            if country_info.get('name_zh') or country_info.get('name_en'):
                countries.append(country_info)
                
    except ET.ParseError:
        # 如果 XML 解析失败，尝试用正则表达式提取
        print("XML 解析失败，尝试使用正则表达式...")
        countries = extract_countries_with_regex(file_path)
    
    return countries

def extract_countries_with_regex(file_path: str) -> List[Dict[str, str]]:
    """
    使用正则表达式从 SVG 文件中提取国家信息
    
    Args:
        file_path: SVG 文件路径
        
    Returns:
        包含所有国家信息的字典列表
    """
    countries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 正则表达式匹配 path 标签及其属性
        # 这个正则表达式会匹配整个 path 标签
        path_pattern = r'<path\s+[^>]*>'
        
        paths = re.findall(path_pattern, content, re.IGNORECASE)
        
        for path_tag in paths:
            country_info = {}
            
            # 提取 id 属性
            id_match = re.search(r'id="([^"]*)"', path_tag)
            if id_match:
                country_info['id'] = id_match.group(1)
            
            # 提取各个 data-* 属性
            name_zh_match = re.search(r'data-name_zht="([^"]*)"', path_tag)
            if name_zh_match:
                country_info['name_zh'] = name_zh_match.group(1)
            else:
                # 如果没有 data-name_zht，尝试 data-name_zh
                name_zh_match = re.search(r'data-name_zh="([^"]*)"', path_tag)
                if name_zh_match:
                    country_info['name_zh'] = name_zh_match.group(1)
                elif country_info.get('id'):
                    country_info['name_zh'] = country_info['id']
            
            name_en_match = re.search(r'data-name_en="([^"]*)"', path_tag)
            if name_en_match:
                country_info['name_en'] = name_en_match.group(1)
            
            formal_en_match = re.search(r'data-formal_en="([^"]*)"', path_tag)
            if formal_en_match:
                country_info['formal_en'] = formal_en_match.group(1)
            
            type_match = re.search(r'data-type="([^"]*)"', path_tag)
            if type_match:
                country_info['type'] = type_match.group(1)
            
            sovereignty_match = re.search(r'data-sovereignt="([^"]*)"', path_tag)
            if sovereignty_match:
                country_info['sovereignty'] = sovereignty_match.group(1)
            
            # 只添加有有效信息的国家
            if country_info.get('name_zh') or country_info.get('name_en'):
                countries.append(country_info)
                
    except Exception as e:
        print(f"读取文件失败: {e}")
    
    return countries

def save_to_json(countries: List[Dict[str, str]], output_file: str = 'countries.json'):
    """
    将国家信息保存为 JSON 文件
    
    Args:
        countries: 国家信息列表
        output_file: 输出文件路径
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(countries, f, ensure_ascii=False, indent=2)
        print(f"国家信息已保存到 {output_file}")
    except Exception as e:
        print(f"保存文件失败: {e}")

def save_to_csv(countries: List[Dict[str, str]], output_file: str = 'countries.csv'):
    """
    将国家信息保存为 CSV 文件
    
    Args:
        countries: 国家信息列表
        output_file: 输出文件路径
    """
    try:
        import csv
        
        # 获取所有可能的字段
        all_fields = set()
        for country in countries:
            all_fields.update(country.keys())
        
        fields = ['id', 'name_zh', 'name_en', 'formal_en', 'type', 'sovereignty']
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            for country in countries:
                # 确保每行都有所有字段
                row = {field: country.get(field, '') for field in fields}
                writer.writerow(row)
        
        print(f"国家信息已保存到 {output_file}")
    except ImportError:
        print("需要安装 csv 模块")
    except Exception as e:
        print(f"保存 CSV 文件失败: {e}")

def print_countries_table(countries: List[Dict[str, str]], limit: Optional[int] = None):
    """
    以表格形式打印国家信息
    
    Args:
        countries: 国家信息列表
        limit: 限制打印的数量，None 表示打印全部
    """
    if limit:
        display_countries = countries[:limit]
    else:
        display_countries = countries
    
    print(f"找到 {len(countries)} 个国家/地区")
    print("-" * 120)
    print(f"{'序号':<4} {'中文名':<12} {'英文名':<20} {'类型':<15} {'主权':<20}")
    print("-" * 120)
    
    for i, country in enumerate(display_countries, 1):
        name_zh = country.get('name_zh', '')[:10]
        name_en = country.get('name_en', '')[:18]
        country_type = country.get('type', '')[:13]
        sovereignty = country.get('sovereignty', '')[:18]
        print(f"{i:<4} {name_zh:<12} {name_en:<20} {country_type:<15} {sovereignty:<20}")
    
    if limit and len(countries) > limit:
        print(f"... 还有 {len(countries) - limit} 个国家未显示")

def main():
    # 设置 SVG 文件路径
    svg_file_path = "世界地图.svg"  # 替换为你的 SVG 文件路径
    
    # 提取国家信息
    print("正在从 SVG 文件中提取国家信息...")
    countries = extract_countries_from_svg(svg_file_path)
    
    if countries:
        print(f"\n成功提取了 {len(countries)} 个国家/地区的信息")
        
        # 显示前 10 个国家作为示例
        print("\n前 10 个国家/地区信息:")
        print_countries_table(countries, limit=10)
        
        # 保存为 JSON 文件
        save_to_json(countries, 'countries.json')
        
        # 保存为 CSV 文件
        save_to_csv(countries, 'countries.csv')
        
        # 统计不同类型
        print("\n国家/地区类型统计:")
        type_counts = {}
        for country in countries:
            country_type = country.get('type', '未知')
            type_counts[country_type] = type_counts.get(country_type, 0) + 1
        
        for country_type, count in sorted(type_counts.items()):
            print(f"  {country_type}: {count}个")
        
        # 查找特定国家
        print("\n查找国家示例:")
        search_terms = ['中国', '美国', '日本', '印度尼西亚']
        for term in search_terms:
            found = [c for c in countries if term in c.get('name_zh', '') or term in c.get('name_en', '')]
            if found:
                print(f"  找到 '{term}': {found[0].get('name_zh')} ({found[0].get('name_en')})")
            else:
                print(f"  未找到 '{term}'")
    else:
        print("未找到任何国家信息，请检查 SVG 文件格式")

if __name__ == "__main__":
    main()