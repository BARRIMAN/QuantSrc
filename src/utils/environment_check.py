"""
环境检查脚本
用于验证项目环境是否正确配置
"""

import sys
import pkg_resources
import importlib

def check_python_version():
    """检查Python版本"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"错误: Python版本需要 >= {required_version[0]}.{required_version[1]}")
        print(f"当前版本: {current_version[0]}.{current_version[1]}")
        return False
    return True

def check_required_packages():
    """检查必需的包是否已安装"""
    required_packages = {
        'numpy': '1.21.0',
        'pandas': '1.3.0',
        'matplotlib': '3.4.0',
        'plotly': '5.3.0',
        'yfinance': '0.1.63',
        'ta-lib': '0.4.24',
        'backtrader': '1.9.76.123',
        'ccxt': '2.0.0',
        'scikit-learn': '0.24.2',
        'python-dotenv': '0.19.0',
        'jupyter': '1.0.0'
    }
    
    missing_packages = []
    outdated_packages = []
    
    for package, version in required_packages.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(version):
                outdated_packages.append((package, installed_version, version))
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
    
    return missing_packages, outdated_packages

def check_data_directory():
    """检查数据目录是否存在并包含必要文件"""
    import os
    from pathlib import Path
    
    data_dir = Path('src/data')
    if not data_dir.exists():
        print("错误: 数据目录不存在")
        return False
    
    required_files = ['BTCUSDT_1d_2021_2025_cleaned.csv']
    missing_files = [f for f in required_files if not (data_dir / f).exists()]
    
    if missing_files:
        print(f"警告: 以下数据文件缺失: {', '.join(missing_files)}")
        return False
    return True

def main():
    """主函数"""
    print("开始环境检查...\n")
    
    # 检查Python版本
    print("检查Python版本...")
    if not check_python_version():
        return False
    print("Python版本检查通过\n")
    
    # 检查必需的包
    print("检查必需的包...")
    missing_packages, outdated_packages = check_required_packages()
    
    if missing_packages:
        print(f"错误: 以下包未安装: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    if outdated_packages:
        print("警告: 以下包版本过低:")
        for package, current, required in outdated_packages:
            print(f"  - {package}: 当前版本 {current}, 需要版本 >= {required}")
        print("建议更新到最新版本")
    
    print("包检查完成\n")
    
    # 检查数据目录
    print("检查数据目录...")
    if not check_data_directory():
        print("数据目录检查未通过")
        return False
    print("数据目录检查通过\n")
    
    print("环境检查完成！")
    return True

if __name__ == '__main__':
    main() 