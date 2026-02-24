# TAGGER / photo_tagging

一个面向个人摄影整理场景的本地照片标签工具。  
它使用桌面图形界面（Tkinter）管理照片标签、查看拍摄参数，并在本地保存索引数据。

## 功能简介

- 导入本地照片文件（支持常见图片格式）
- 自动读取拍摄时间与常见 EXIF 信息（机身、镜头、焦距、快门、ISO 等）
- 自动生成缩略图并在网格中浏览
- 支持多选照片并批量添加标签
- 按“未标签 / 指定标签”快速筛选照片
- 双击查看照片详情，右键可删除照片记录或全局移除标签
- 可配置焦距显示模式（关闭 / 总是 ×1.5 / 自动按机身判断）

> 说明：本工具删除的是索引记录与缩略图，不会删除原始照片文件。

## 下载方式

你可以通过以下任一方式获取项目：

1. **Git 克隆（推荐）**

   ```bash
   git clone https://github.com/gracezhouxinyuan/photo_tagging.git
   cd photo_tagging
   ```

2. **下载 ZIP**
   - 打开仓库主页：`https://github.com/gracezhouxinyuan/photo_tagging`
   - 点击 `Code` -> `Download ZIP`
   - 解压后进入项目目录

## 环境要求

- Python 3.10+（建议）
- 操作系统：macOS（当前代码中包含 `open -R` 的 Finder 行为）
- 依赖：
  - `Pillow`（用于读取 EXIF 与生成缩略图）

安装依赖示例：

```bash
pip install Pillow
```

## 快速开始

在项目根目录运行：

```bash
python main_app.py
```

启动后可按以下流程操作：

1. 点击「导入…」选择照片
2. 在主界面中单击选择照片（可多选）
3. 在标签输入框中输入标签（英文逗号或中文逗号分隔）并点击「添加」
4. 在左侧标签列表中切换筛选，双击照片可查看详细信息

## 数据存储位置

程序会在本地用户目录写入数据（默认）：

- 索引文件：`~/Library/Application Support/TAGGER/library_index.json`
- 设置文件：`~/Library/Application Support/TAGGER/settings.json`
- 缩略图缓存：`~/Library/Application Support/TAGGER/ThumbCache/`

## 常见问题（FAQ）

### 1) 为什么看不到缩略图或 EXIF？

通常是因为未安装 `Pillow`，请先执行：

```bash
pip install Pillow
```

### 2) 删除照片会删掉原图吗？

不会。当前删除操作仅移除 TAGGER 的本地索引记录（以及对应缩略图缓存），不删除原始图片文件。

### 3) 可以一次添加多个标签吗？

可以。在输入框中使用英文逗号 `,` 或中文逗号 `，` 分隔多个标签即可。
