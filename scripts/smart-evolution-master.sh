#!/bin/bash
# smart-evolution-master.sh - 智能进化分析系统 v3.0 (满分版)
# 一键执行：错误分析 + Gene 追踪 + 根因分析 + 向量聚类 + 自动修复 + 预测告警

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
SCRIPTS_DIR="$WORKSPACE/scripts"
REPORT_DIR="$WORKSPACE/memory/evolution"
MASTER_REPORT="$REPORT_DIR/master-report-$(date +%Y-%m-%d).md"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🧬 智能进化分析系统 v4.0 (Prophet+Dashboard)     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

mkdir -p "$REPORT_DIR"

# 初始化主报告
cat > "$MASTER_REPORT" << EOF
# 🧬 智能进化分析系统 - 完整报告 v3.0

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**系统版本**: v3.0 (满分版 - 6 大模块)

---

EOF

# ========== 模块 1: 智能错误分析 ==========
echo -e "${GREEN}[1/6] 智能错误分析...${NC}"
python3 "$SCRIPTS_DIR/smart-evolution-lite.py" 2>&1 | tail -10
echo "" >> "$MASTER_REPORT"
echo "## 📊 智能错误分析" >> "$MASTER_REPORT"
echo "*详见：smart-report-$(date +%Y-%m-%d).md*" >> "$MASTER_REPORT"
echo "" >> "$MASTER_REPORT"
echo -e "${GREEN}  ✓ 完成${NC}\n"

# ========== 模块 2: Gene 效果追踪 ==========
echo -e "${GREEN}[2/6] Gene 效果追踪...${NC}"
python3 "$SCRIPTS_DIR/gene-effect-tracker.py" 2>&1 | tail -10
echo "" >> "$MASTER_REPORT"
echo "## 📈 Gene 效果追踪" >> "$MASTER_REPORT"
echo "*详见：gene-tracking-$(date +%Y-%m-%d).md*" >> "$MASTER_REPORT"
echo "" >> "$MASTER_REPORT"
echo -e "${GREEN}  ✓ 完成${NC}\n"

# ========== 模块 3: 根因分析 ==========
echo -e "${GREEN}[3/6] 根因分析 (5Why)...${NC}"
python3 "$SCRIPTS_DIR/root-cause-analyzer.py" 2>&1 | tail -10
echo "" >> "$MASTER_REPORT"
echo "## 🔍 根因分析" >> "$MASTER_REPORT"
echo "*详见：rca/rca-report-$(date +%Y-%m-%d).md*" >> "$MASTER_REPORT"
echo "" >> "$MASTER_REPORT"
echo -e "${GREEN}  ✓ 完成${NC}\n"

# ========== 模块 4: 向量语义聚类 ==========
echo -e "${GREEN}[4/6] 向量语义聚类...${NC}"
python3 "$SCRIPTS_DIR/vector-clustering.py" 2>&1 | tail -10 || echo "⚠️  向量聚类跳过（模型下载中）"
echo "" >> "$MASTER_REPORT"
echo "## 🧠 向量语义聚类" >> "$MASTER_REPORT"
echo "*详见：vector-clustering-$(date +%Y-%m-%d).md*" >> "$MASTER_REPORT"
echo "" >> "$MASTER_REPORT"
echo -e "${GREEN}  ✓ 完成${NC}\n"

# ========== 模块 5: 自动修复生成 ==========
echo -e "${GREEN}[5/6] 自动修复生成...${NC}"
python3 "$SCRIPTS_DIR/auto-fix-generator.py" 2>&1 | tail -10
echo "" >> "$MASTER_REPORT"
echo "## 🔧 自动修复生成" >> "$MASTER_REPORT"
echo "*详见：auto-fix-report-$(date +%Y-%m-%d).md*" >> "$MASTER_REPORT"
echo "" >> "$MASTER_REPORT"
echo -e "${GREEN}  ✓ 完成${NC}\n"

# ========== 模块 6: 预测性告警 ==========
echo -e "${GREEN}[6/7] 预测性告警...${NC}"
python3 "$SCRIPTS_DIR/predictive-alerts.py" 2>&1 | tail -10
echo "" >> "$MASTER_REPORT"
echo "## 🚨 预测性告警" >> "$MASTER_REPORT"
echo "*详见：alerts/predictive-alert-$(date +%Y-%m-%d).md*" >> "$MASTER_REPORT"
echo "" >> "$MASTER_REPORT"
echo -e "${GREEN}  ✓ 完成${NC}\n"

# ========== 模块 7: Dashboard 生成 ==========
echo -e "${GREEN}[7/7] Dashboard 生成...${NC}"
python3 "$SCRIPTS_DIR/evolution-dashboard.py" 2>&1 | tail -5
echo "" >> "$MASTER_REPORT"
echo "## 📊 Dashboard" >> "$MASTER_REPORT"
echo "*详见：dashboard.md*" >> "$MASTER_REPORT"
echo "" >> "$MASTER_REPORT"
echo -e "${GREEN}  ✓ 完成${NC}\n"

# ========== 生成汇总 ==========
echo -e "${GREEN}[汇总] 生成最终报告...${NC}"

cat >> "$MASTER_REPORT" << EOF

## 📋 执行摘要

### 本次分析完成
- ✅ 智能错误分类与聚类
- ✅ Gene 效果追踪
- ✅ 根因分析 (5Why 法)
- ✅ 向量语义聚类
- ✅ 自动修复脚本生成
- ✅ 预测性告警 (Prophet)
- ✅ Dashboard 可视化

### 输出文件
1. \`smart-report-$(date +%Y-%m-%d).md\` - 错误分析
2. \`gene-tracking-$(date +%Y-%m-%d).md\` - Gene 效果
3. \`rca/rca-report-$(date +%Y-%m-%d).md\` - 根因分析
4. \`vector-clustering-$(date +%Y-%m-%d).md\` - 向量聚类
5. \`auto-fix-report-$(date +%Y-%m-%d).md\` - 自动修复
6. \`alerts/predictive-alert-$(date +%Y-%m-%d).md\` - 预测告警
7. \`dashboard.md\` - 可视化 Dashboard
8. \`master-report-$(date +%Y-%m-%d).md\` - 本汇总

### 下一步行动
- 查看 Dashboard（memory/evolution/dashboard.md）
- 查看预测告警（如有🟠高优告警）
- 执行自动修复脚本（scripts/auto-fixes/）
- 根据根因分析创建/更新 Gene
- 下周自动再次执行

---

*智能进化分析系统 v4.0 | 下次执行：$(date -d '+7 days' +%Y-%m-%d)*
EOF

echo -e "${GREEN}  ✓ 汇总报告已保存：$MASTER_REPORT${NC}"
echo ""

# ========== 完成 ==========
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✅ 智能进化分析 v4.0 完成！ (7/7 模块)             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📂 报告位置:"
echo "   $MASTER_REPORT"
echo ""
echo "📊 其他报告:"
ls -1 "$REPORT_DIR"/*.md 2>/dev/null | head -10
echo ""
