# 使用示例

## 示例1：跨AI工具写文章

### 在豆包里创建接棒

```bash
handoff create "写公众号第一篇文章初稿" \
  --completed "标题、大纲、风格已定，配图6张已做好" \
  --todo "全文初稿3000字，按大纲写" \
  --notes "简洁优雅，柴静式叙事，避免AI黑话；配图用希腊雕塑风" \
  --files "文章大纲：https://feishu.doubao.com/docx/xxx" \
  --project "公众号文章" \
  --tags "写作,发布"
```

### 在WorkBuddy里接受并完成

```bash
# 接受接棒
handoff accept

# 写完后完成
handoff complete \
  --output "初稿已写完，存在 https://feishu.doubao.com/docx/yyy" \
  --notes "第三节案例待补充，建议用户提供真实数据"
```

### 回到豆包继续

```bash
handoff accept
# 自动读到WorkBuddy完成了什么，直接开始改稿
```

---

## 示例2：多设备写代码

### 公司电脑上创建接棒

```bash
handoff create "实现用户登录功能" \
  --completed "数据库表结构已设计，API接口已定义" \
  --todo "编写登录接口、JWT token生成、前端登录页面" \
  --notes "用FastAPI，密码用bcrypt加密" \
  --files "代码仓库：https://github.com/xxx/project" \
  --project "用户系统" \
  --tags "后端,登录"
```

### 同步到家里电脑

```bash
# 把 ~/.handoff 目录同步到Git或云盘
cd ~/.handoff
git add -A && git commit -m "handoff update" && git push
```

### 家里电脑上继续

```bash
cd ~/.handoff && git pull
handoff accept
# 开始写代码
```

---

## 示例3：MCP配置

### Claude Code

在 `~/.claude.json` 中添加：

```json
{
  "mcpServers": {
    "handoff": {
      "command": "handoff",
      "args": ["serve"]
    }
  }
}
```

然后直接跟Claude说：
- "帮我创建接棒，这个功能交给下一个AI继续"
- "接棒，看看有什么待办"
- "完成接棒，记录一下产出"

### Cursor

在 Cursor 设置 → MCP 中添加同样的配置。
