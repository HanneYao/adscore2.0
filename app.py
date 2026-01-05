import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import json
import datetime
import socket

# --- 确保 Flask 能找到 HTML ---
# 将 app 实例化改为如下代码, index.html 放在 templates 文件夹
app = Flask(__name__, template_folder='templates') 
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 打印详细的启动信息
print("=" * 60)
print("广告内容效果评分系统后端 - 合并版")
print("=" * 60)

# 获取本机IP地址
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"本机IP地址: {local_ip}")
except:
    local_ip = "无法获取"

print(f"当前工作目录: {os.getcwd()}")
print("=" * 60)

# 检查文件是否存在
required_files = ['templates/index.html', 'generated_population_data.csv']
for file in required_files:
    exists = os.path.exists(file)
    status = "✓ 存在" if exists else "✗✗ 缺失"
    print(f"{file}: {status}")

print("=" * 60)

# 主题标签映射（从TXT文件解析的）
THEME_MAPPING = {
    "中长视频类": [
        "情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", 
        "自我态度表达", "幽默潮流娱乐", "产品功能主张", "家庭与私密空间",
        "消费商业街区", "生产学习空间", "城市公共空间", "自然与户外探索",
        "虚拟与虚构空间", "温暖治愈", "幽默魔性", "轻松明快", 
        "高级质感", "热血励志", "科技酷感", "理性客观", 
        "质朴真诚", "悬疑紧张", "人文厚重", "文艺清新"
    ],
    "短视频类": [
        "情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", 
        "自我态度表达", "幽默潮流娱乐", "产品功能主张", "家庭与私密空间",
        "消费商业街区", "生产学习空间", "城市公共空间", "自然与户外探索",
        "虚拟与虚构空间"
    ],
    "图文类": [
        "情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", 
        "自我态度表达", "幽默潮流娱乐", "产品功能主张", "温馨感动",
        "轻松愉悦", "向往憧憬", "认同归属", "震撼惊奇", 
        "安心信任", "理性信服", "好奇探索", "价值激励"
    ],
    "平面类": [
        "情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", 
        "自我态度表达", "幽默潮流娱乐", "产品功能主张", "温馨感动",
        "轻松愉悦", "向往憧憬", "认同归属", "震撼惊奇", 
        "安心信任", "理性信服", "好奇探索", "价值激励"
    ],
    "动画类": [
        "情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", 
        "自我态度表达", "幽默潮流娱乐", "产品功能主张"
    ],
    "声音类": [
        "情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", 
        "自我态度表达", "幽默潮流娱乐", "产品功能主张", "软广", "硬广"
    ],
    "直播带货类": [
        "背景板直播间及虚拟场景", "源头场景", "生产场景", "实体卖场场景",
        "户外移动场景", "产品介绍", "场景代入", "角色扮演", "故事叙事", "用户证言"
    ]
}

# 维度映射
DIMENSION_MAPPING = {
    "中长视频类": ["主题", "场景", "调性"],
    "短视频类": ["主题", "场景"],
    "图文类": ["主题", "情绪唤起"],
    "平面类": ["主题", "情绪唤起"],
    "动画类": ["主题"],
    "声音类": ["主题", "软硬"],
    "直播带货类": ["场景维度", "叙事风格"]
}

# 维度-标签映射
DIMENSION_TAG_MAPPING = {
    "中长视频类": {
        "主题": ["情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", "自我态度表达", "幽默潮流娱乐", "产品功能主张"],
        "场景": ["家庭与私密空间", "消费商业街区", "生产学习空间", "城市公共空间", "自然与户外探索", "虚拟与虚构空间"],
        "调性": ["温暖治愈", "幽默魔性", "轻松明快", "高级质感", "热血励志", "科技酷感", "理性客观", "质朴真诚", "悬疑紧张", "人文厚重", "文艺清新"]
    },
    "短视频类": {
        "主题": ["情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", "自我态度表达", "幽默潮流娱乐", "产品功能主张"],
        "场景": ["家庭与私密空间", "消费商业街区", "生产学习空间", "城市公共空间", "自然与户外探索", "虚拟与虚构空间"]
    },
    "图文类": {
        "主题": ["情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", "自我态度表达", "幽默潮流娱乐", "产品功能主张"],
        "情绪唤起": ["温馨感动", "轻松愉悦", "向往憧憬", "认同归属", "震撼惊奇", "安心信任", "理性信服", "好奇探索", "价值激励"]
    },
    "平面类": {
        "主题": ["情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", "自我态度表达", "幽默潮流娱乐", "产品功能主张"],
        "情绪唤起": ["温馨感动", "轻松愉悦", "向往憧憬", "认同归属", "震撼惊奇", "安心信任", "理性信服", "好奇探索", "价值激励"]
    },
    "动画类": {
        "主题": ["情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", "自我态度表达", "幽默潮流娱乐", "产品功能主张"]
    },
    "声音类":{
        "主题": ["情感关系联结", "社会洞察关怀", "文化价值联结", "生活方式理念", "自我态度表达", "幽默潮流娱乐", "产品功能主张"],
        "软硬": ["软广", "硬广"]
    },
    "直播带货类": {
        "场景维度": ["背景板直播间及虚拟场景", "源头场景", "生产场景", "实体卖场场景", "户外移动场景"],
        "叙事风格": ["产品介绍", "场景代入", "角色扮演", "故事叙事", "用户证言"]
    }
}

# 广告类型列表（合并后的新类型）
AD_TYPES = list(THEME_MAPPING.keys()) + ["互动类", "裂变类", "赞助类", "植入类"]

# 全局变量存储用户偏好数据和内容表达数据两个数据源
user_preference_data = None # generated_population_data.csv
content_expression_data = None  # content_tag_values.csv
csv_loaded = False
csv_error = None

def load_both_data_sources():
    global user_preference_data, content_expression_data, csv_loaded, csv_error
    
    try:
        # 1. 加载用户偏好数据
        print("正在加载 generated_population_data.csv...")
        # 使用 os.path.join 组合路径
        pref_path = os.path.join(BASE_DIR, 'generated_population_data.csv')
        df_pref = pd.read_csv(pref_path)
        print(f"用户偏好数据形状: {df_pref.shape}")
        print(f"列名: {list(df_pref.columns)}")
        
        # 计算每列的平均值（Pavg）
        column_means = {}
        for column in df_pref.columns:
            if pd.api.types.is_numeric_dtype(df_pref[column]):
                column_means[column] = float(df_pref[column].mean())
            else:
                print(f"跳过非数值列: {column}")
        
        user_preference_data = column_means
        print(f"成功加载 {len(user_preference_data)} 个数值列的平均值")
        
        # 2. 加载内容表达度数据
        print("正在加载 content_tag_values.csv...")
        content_path = os.path.join(BASE_DIR, 'content_tag_values.csv')
        df_content = pd.read_csv(content_path)
        print(f"内容表达度数据形状: {df_content.shape}")
        print(f"列名: {list(df_content.columns)}")
        
        content_expression_data = {}
        for index, row in df_content.iterrows():
            if len(row) > 0:
                ad_type = str(row.iloc[0]).strip()  # 第一列为广告类型
                content_expression_data[ad_type] = {}
                
                for i in range(1, len(row)):
                    if i < len(df_content.columns):
                        tag = df_content.columns[i]
                        try:
                            content_expression_data[ad_type][tag] = float(row.iloc[i])
                        except (ValueError, TypeError):
                            content_expression_data[ad_type][tag] = 0.5  # 默认值
        
        print(f"成功加载 {len(content_expression_data)} 个广告类型的内容表达度")
        
        csv_loaded = True
        csv_error = None
        return True
    
    except Exception as e:
        csv_error = f"数据加载失败: {str(e)}"
        csv_loaded = False
        print(f"错误详情: {csv_error}")
        import traceback
        traceback.print_exc()
        return False

    # 修正后的计算逻辑
def calculate_match_value(ad_type, tags_with_weights):
    """
    修正的匹配值计算：同时考虑用户偏好(Pavg)和内容表达度
    tags_with_weights: [(tag1, weight1), (tag2, weight2), ...]
    """
    total_match = 0
    total_weight = 0
    
    for tag, weight in tags_with_weights:
        # 构建列名获取用户偏好值（Pavg）
        column_name = f"{ad_type}–{tag}"
        pavg = user_preference_data.get(column_name, 0.5)  # 默认0.5
        
        # 获取内容表达度
        expression_value = content_expression_data.get(ad_type, {}).get(tag, 0.5)  # 默认0.5
        
        # 计算该标签的匹配贡献：Pavg × 表达度 × 权重
        tag_contribution = pavg * expression_value * weight
        total_match += tag_contribution
        total_weight += weight
    
    # 归一化处理
    if total_weight > 0:
        return total_match / total_weight
    else:
        return 0.5  # 默认值

# 初始化时加载数据
if os.path.exists('generated_population_data.csv') and os.path.exists('content_tag_values.csv'):
    csv_loaded = load_both_data_sources()
else:
    print("⚠️  CSV文件不存在，将在首次请求时尝试加载")

# 主页路由
@app.route('/')
def index():
    return render_template('index.html')

# API路由
@app.route('/api/theme-tags', methods=['GET'])
def get_theme_tags():
    return jsonify({
        'success': True,
        'theme_mapping': THEME_MAPPING,
        'ad_types': AD_TYPES
    })

@app.route('/api/data-status', methods=['GET'])
def get_data_status():
    """返回更详细的数据文件状态信息"""
    files_status = {
        'generated_population_data.csv': {
            'exists': os.path.exists('generated_population_data.csv'),
            'size': os.path.getsize('generated_population_data.csv') if os.path.exists('generated_population_data.csv') else 0
        },
        'content_tag_values.csv': {
            'exists': os.path.exists('content_tag_values.csv'),
            'size': os.path.getsize('content_tag_values.csv') if os.path.exists('content_tag_values.csv') else 0
        }
    }
    
    all_files_exist = files_status['generated_population_data.csv']['exists'] and files_status['content_tag_values.csv']['exists']
    
    return jsonify({
        'success': all_files_exist,
        'files_status': files_status,
        'all_files_exist': all_files_exist,
        'user_preference_loaded': user_preference_data is not None,
        'content_expression_loaded': content_expression_data is not None
    })

# 修改API路由，提供更详细的错误信息
@app.route('/api/preference-data', methods=['GET'])
def get_preference_data():
    global csv_loaded, csv_error
    
    if not csv_loaded:
        load_both_data_sources()
    
    if csv_loaded and user_preference_data is not None:
        return jsonify({
            'success': True,
            'data_loaded': True,
            'column_count': len(user_preference_data),
            'user_preference_columns': list(user_preference_data.keys())[:10],  # 返回前10个列名用于调试
            'content_expression_types': list(content_expression_data.keys()) if content_expression_data else []
        })
    else:
        # 提供详细的错误信息
        error_info = {
            'success': False,
            'error': csv_error or 'CSV数据未加载',
            'data_loaded': False,
            'files_checked': {
                'generated_population_data.csv': os.path.exists('generated_population_data.csv'),
                'content_tag_values.csv': os.path.exists('content_tag_values.csv')
            }
        }
        return jsonify(error_info)
    
# 添加调试接口
@app.route('/api/debug-files', methods=['GET'])
def debug_files():
    """返回文件详细信息和前几行数据"""
    result = {}
    
    for filename in ['generated_population_data.csv', 'content_tag_values.csv']:
        file_info = {
            'exists': os.path.exists(filename),
            'size': os.path.getsize(filename) if os.path.exists(filename) else 0
        }
        
        if file_info['exists']:
            try:
                df = pd.read_csv(filename, nrows=5)  # 只读取前5行
                file_info['shape'] = df.shape
                file_info['columns'] = list(df.columns)
                file_info['sample_data'] = df.head(2).to_dict('records')
            except Exception as e:
                file_info['read_error'] = str(e)
        
        result[filename] = file_info
    
    return jsonify(result)

@app.route('/api/calculate-score', methods=['POST'])
def calculate_score():
    try:
        data = request.json
        
        # 获取参数
        base_score = float(data.get('base_score', 100)) / 100
        ad_type = data.get('ad_type', '')
        alpha = float(data.get('alpha', 0.5))
        
        # 获取前端传来的带有权重的维度数据
        # 结构: { "主题": [ {"tag": "标签A", "weight": 0.6}, ... ], ... }
        dimensions_data = data.get('dimensions', {}) 
        
        if not ad_type:
            return jsonify({'success': False, 'error': '请选择广告类型'})
        
        # 检查是否至少有一个维度有标签
        total_tags = 0
        for dim, tags in dimensions_data.items():
            total_tags += len(tags)
        
        if total_tags == 0:
            return jsonify({'success': False, 'error': '请至少选择一个标签'})
        
        # 计算每个主题的匹配值
        dimension_match_values = []
        formula_detail = ""
        
        for dimension, tag_objects in dimensions_data.items():
            if len(tag_objects) == 0:
                continue
                
            dim_match = 0
            dim_formula = f"{dimension}维度: "
            
            # 遍历前端传来的带有权重的对象
            for i, item in enumerate(tag_objects):
                tag_name = item['tag']
                weight = float(item['weight']) # 直接使用前端计算的权重
                
                # 构建列名获取表达度（用户偏好值）
                column_name = f"{ad_type}–{tag_name}"
                expression_value = user_preference_data.get(column_name, 0.5)  # 默认0.5
                
                dim_match += expression_value * weight
                dim_formula += f"{tag_name}(值:{expression_value:.3f}×权:{weight:.2f})"
                if i < len(tag_objects) - 1:
                    dim_formula += " + "
            
            dimension_match_values.append(dim_match)
            formula_detail += f"{dim_formula} = {dim_match:.3f}\n"
        
         # 计算总匹配值（各维度平均值）
        if dimension_match_values:
            match_value = sum(dimension_match_values) / len(dimension_match_values)
        else:
            match_value = 0.5
        
        # 计算加成系数k
        k = 1 + alpha * (match_value - 0.5)
        
        # 计算最终得分
        final_score = base_score * k
        
        return jsonify({
            'success': True,
            'data_source': 'CSV用户偏好数据 + 动态权重',
            'results': {
                'base_score': base_score * 100,
                'match_value': match_value,
                'k': k,
                'final_score': final_score * 100
            },
            'dimensions_used': dimensions_data,
            'ad_type': ad_type
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'计算错误: {str(e)}'
        })
    
# 添加新的API端点获取维度信息
@app.route('/api/dimension-tags', methods=['GET'])
def get_dimension_tags():
    ad_type = request.args.get('ad_type', '')
    if not ad_type or ad_type not in DIMENSION_TAG_MAPPING:
        return jsonify({'success': False, 'error': '无效的广告类型'})
    
    return jsonify({
        'success': True,
        'dimensions': DIMENSION_MAPPING.get(ad_type, []),
        'dimension_tags': DIMENSION_TAG_MAPPING.get(ad_type, {})
    })


# 健康检查路由
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0',
        'csv_loaded': csv_loaded,
        'csv_error': csv_error
    })

@app.route('/debug')
def debug_info():
    files = os.listdir('.')
    file_list = '<br>'.join([f"{f} ({'文件' if os.path.isfile(f) else '文件夹'})" for f in files])
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>调试信息</title></head>
    <body>
        <h1>系统调试信息</h1>
        <p><strong>当前时间:</strong> {datetime.datetime.now()}</p>
        <p><strong>工作目录:</strong> {os.getcwd()}</p>
        <p><strong>CSV加载状态:</strong> {csv_loaded}</p>
        <p><strong>CSV错误信息:</strong> {csv_error or '无'}</p>
        <h2>文件列表:</h2>
        {file_list}
        <h2>测试链接:</h2>
        <ul>
            <li><a href="/health">健康检查</a></li>
            <li><a href="/api/theme-tags">主题标签API</a></li>
            <li><a href="/api/preference-data">偏好数据API</a></li>
        </ul>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # 检查是否在 PythonAnywhere 环境中
    if 'PYTHONANYWHERE_DOMAIN' in os.environ:
        # 在生产环境中使用
        app.run(debug=False)
    else:
        # 在开发环境中使用
        print("服务器启动在:")
        print("✓ http://127.0.0.1:5000/ (推荐)")
        print("○ http://localhost:5000/ (如果上面不行)")
        print("=" * 60)
        app.run(debug=True, port=5000, host='127.0.0.1')
