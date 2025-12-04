# 英语课文跟读工具 - 测试说明

## 测试步骤

### 1. 设置页面测试
- 打开 index.html
- 输入测试英语短文
- 输入对应中文释义
- 添加单词详情（格式：单词 音标 词性 释义）
- 上传测试图片
- 调整参数设置
- 点击"开始跟读"

### 2. 跟读页面测试
- 检查词汇统计是否正确
- 验证图片是否正确显示
- 测试播放/暂停功能
- 测试上一句/下一句导航
- 验证中英切换功能
- 点击词汇查看详情
- 测试自动播放功能

### 3. 功能验证
- 语音合成是否正常播放
- 词汇高亮颜色是否正确
- 进度指示是否准确
- 键盘快捷键是否有效
- 数据是否正确保存

## 示例测试数据

### 英语短文
```
Hello! My name is Tom. I am a student from America. I love learning English and making new friends. Today is a beautiful day with sunshine and flowers. I want to go to the park to read books and enjoy nature.
```

### 中文释义
```
你好！我的名字叫汤姆。我是一个来自美国的学生。我喜欢学习英语和交新朋友。今天是美丽的一天，阳光明媚，鲜花盛开。我想去公园看书，享受大自然。
```

### 单词详情
```
hello [həˈləʊ] int. 你好
name [neɪm] n. 名字
student [ˈstjuːdnt] n. 学生
America [əˈmerɪkə] n. 美国
love [lʌv] v. 爱，喜欢
learning [ˈlɜːnɪŋ] n. 学习
English [ˈɪŋɡlɪʃ] n. 英语
making [ˈmeɪkɪŋ] v. 制作，交朋友
friends [frendz] n. 朋友
Today [təˈdeɪ] adv. 今天
beautiful [ˈbjuːtɪfl] adj. 美丽的
sunshine [ˈsʌnʃaɪn] n. 阳光
flowers [ˈflaʊəz] n. 花朵
want [wɒnt] v. 想要
park [pɑːk] n. 公园
read [riːd] v. 阅读
books [bʊks] n. 书籍
enjoy [ɪnˈdʒɔɪ] v. 享受
nature [ˈneɪtʃə] n. 自然
```

## 预期功能表现

1. **设置页面**
   - 实时字符计数
   - 图片上传预览
   - 参数实时调整
   - 表单验证提示

2. **跟读页面**
   - 词汇按频率高亮显示
   - 语音播放流畅
   - 进度实时更新
   - 中英模式切换

3. **交互功能**
   - 点击句子播放
   - 词汇详情弹窗
   - 键盘快捷键
   - 自动播放模式