#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预测性告警系统 v2.0 - Prophet 时间序列预测
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

try:
    from prophet import Prophet
    import pandas as pd
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False
    print("⚠️  Prophet 未安装，降级到线性回归")

WORKSPACE = Path("/root/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE / ".learnings"
ALERTS_DIR = WORKSPACE / "memory/evolution/alerts"


def parse_learning_date(file_path):
    """从文件名提取日期"""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        except:
            pass
    return datetime.now()


def categorize_error(content):
    """分类错误"""
    content_lower = content.lower()
    if any(kw in content_lower for kw in ['api', '接口', '端点']):
        return 'api_error'
    elif any(kw in content_lower for kw in ['配置', 'config']):
        return 'config_error'
    elif any(kw in content_lower for kw in ['数据', '解析', 'json']):
        return 'data_error'
    else:
        return 'other'


def collect_time_series():
    """收集错误时间序列"""
    daily_counts = defaultdict(lambda: defaultdict(int))
    
    if not LEARNINGS_DIR.exists():
        return daily_counts
    
    for file in LEARNINGS_DIR.glob("*.md"):
        try:
            content = file.read_text(encoding='utf-8')
            date = parse_learning_date(file)
            date_str = date.strftime('%Y-%m-%d')
            category = categorize_error(content)
            
            daily_counts[date_str][category] += 1
            daily_counts[date_str]['total'] += 1
        except:
            pass
    
    return daily_counts


def predict_with_prophet(dates, values, category):
    """使用 Prophet 预测"""
    if not HAS_PROPHET or len(dates) < 3:
        return None, None
    
    try:
        # 准备数据
        df = pd.DataFrame({
            'ds': dates,
            'y': values
        })
        
        # 创建模型
        m = Prophet(daily_seasonality=False, weekly_seasonality=False)
        m.fit(df)
        
        # 预测未来 7 天
        future = m.make_future_dataframe(periods=7)
        forecast = m.predict(future)
        
        # 提取预测值
        future_values = forecast['yhat'].tail(7).tolist()
        
        # 计算趋势
        last_week_avg = sum(values[-7:]) / min(7, len(values))
        predicted_avg = sum(future_values) / 7
        
        if predicted_avg > last_week_avg * 1.3:
            trend = "上升"
            severity = "🟠"
        elif predicted_avg > last_week_avg * 1.1:
            trend = "小幅上升"
            severity = "🟡"
        elif predicted_avg < last_week_avg * 0.7:
            trend = "下降"
            severity = "🟢"
        else:
            trend = "平稳"
            severity = "⚪"
        
        return {
            "trend": trend,
            "severity": severity,
            "current": int(last_week_avg),
            "predicted": int(predicted_avg),
            "future_values": future_values,
        }, forecast
    
    except Exception as e:
        print(f"⚠️  Prophet 预测失败：{e}，降级到线性回归")
        return None, None


def simple_linear_regression(dates, values):
    """简单线性回归（备用方案）"""
    if len(dates) < 2:
        return None
    
    n = len(dates)
    sum_x = sum(range(n))
    sum_y = sum(values)
    sum_xy = sum(i * v for i, v in enumerate(values))
    sum_x2 = sum(i*i for i in range(n))
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x + 0.001)
    intercept = (sum_y - slope * sum_x) / n
    
    future_values = [slope * (n + i) + intercept for i in range(7)]
    
    current_avg = sum(values[-3:]) / min(3, len(values))
    predicted_avg = sum(future_values[:3]) / 3
    
    if slope > 0.5:
        trend = "上升"
        severity = "🟠" if slope > 1 else "🟡"
    elif slope < -0.5:
        trend = "下降"
        severity = "🟢"
    else:
        trend = "平稳"
        severity = "⚪"
    
    return {
        "trend": trend,
        "severity": severity,
        "current": int(current_avg),
        "predicted": max(0, int(predicted_avg)),
        "slope": slope,
    }


def generate_alerts(daily_counts):
    """生成告警"""
    alerts = []
    
    sorted_dates = sorted(daily_counts.keys())
    if len(sorted_dates) < 3:
        return alerts
    
    categories = ['total', 'api_error', 'data_error', 'config_error']
    
    for cat in categories:
        values = [daily_counts[d].get(cat, 0) for d in sorted_dates]
        
        # 跳过全零数据
        if sum(values) == 0:
            continue
        
        # 优先使用 Prophet
        if HAS_PROPHET:
            dates_pd = pd.to_datetime(sorted_dates)
            result, _ = predict_with_prophet(dates_pd, values, cat)
        else:
            result = None
        
        # 降级到线性回归
        if result is None:
            result = simple_linear_regression(sorted_dates, values)
        
        if result:
            alerts.append({
                "category": cat,
                **result,
                "message": f"{cat.replace('_', ' ').title()}: 当前 {result.get('current', 0)}/天 → 预测 {result.get('predicted', 0)}/天",
            })
    
    return alerts


def generate_report(alerts, daily_counts):
    """生成报告"""
    report = ["# 🚨 预测性告警报告 v2.0", ""]
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**分析数据**: {len(daily_counts)} 天")
    report.append(f"**预测引擎**: {'Prophet ✅' if HAS_PROPHET else '线性回归 ⚠️'}")
    report.append("")
    
    # 告警摘要
    report.append("## ⚠️ 告警摘要")
    report.append("")
    
    if alerts:
        for alert in alerts:
            report.append(f"{alert['severity']} {alert['message']}")
        report.append("")
    else:
        report.append("✅ 无异常告警 - 所有错误类型趋势平稳或下降")
        report.append("")
    
    # 详细趋势
    report.append("## 📈 详细趋势分析")
    report.append("")
    
    sorted_dates = sorted(daily_counts.keys())[-14:]
    for cat in ['total', 'api_error', 'data_error', 'config_error']:
        values = [daily_counts[d].get(cat, 0) for d in sorted_dates]
        if any(v > 0 for v in values):
            report.append(f"### {cat.replace('_', ' ').title()}")
            report.append(f"最近 14 天：{' → '.join(str(v) for v in values[-7:])}")
            
            # 添加预测
            alert = next((a for a in alerts if a['category'] == cat), None)
            if alert:
                report.append(f"预测趋势：{alert['trend']}")
                report.append(f"7 天后预测：{alert.get('predicted', 'N/A')}/天")
            report.append("")
    
    # 建议行动
    report.append("## 💡 建议行动")
    report.append("")
    
    critical = [a for a in alerts if a['severity'] == '🟠']
    if critical:
        report.append("### 🟠 高优先级")
        for alert in critical:
            report.append(f"- {alert['category']}: 建议立即分析根因并创建 Gene")
        report.append("")
    
    warning = [a for a in alerts if a['severity'] == '🟡']
    if warning:
        report.append("### 🟡 中优先级")
        for alert in warning:
            report.append(f"- {alert['category']}: 建议本周内分析")
        report.append("")
    
    if not alerts:
        report.append("✅ 当前无需特殊行动，继续监控即可")
        report.append("")
    
    report.append("---")
    report.append(f"*预测模型：{'Prophet 时间序列' if HAS_PROPHET else '简单线性回归'} | 预测周期：7 天*")
    
    return '\n'.join(report)


def run():
    """主流程"""
    print("=" * 50)
    print("🚨 预测性告警系统 v2.0")
    print("=" * 50)
    print()
    
    # 收集时间序列
    print("📊 收集错误时间序列...")
    daily_counts = collect_time_series()
    print(f"  ✓ 收集 {len(daily_counts)} 天数据")
    print()
    
    # 生成告警
    print(f"🔍 分析趋势（引擎：{'Prophet' if HAS_PROPHET else '线性回归'}）...")
    alerts = generate_alerts(daily_counts)
    
    if alerts:
        print(f"  ⚠️  生成 {len(alerts)} 条告警")
    else:
        print("  ✓ 无异常告警")
    print()
    
    # 生成报告
    print("📝 生成报告...")
    report = generate_report(alerts, daily_counts)
    
    ALERTS_DIR.mkdir(exist_ok=True)
    report_file = ALERTS_DIR / f"predictive-alert-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"  ✓ 报告已保存：{report_file}")
    print()
    
    # 输出摘要
    print("=" * 50)
    print("📋 告警摘要")
    print("=" * 50)
    
    if alerts:
        for alert in alerts:
            print(f"{alert['severity']} {alert['message']}")
    else:
        print("✅ 所有错误类型趋势平稳")
    print()


if __name__ == "__main__":
    run()
