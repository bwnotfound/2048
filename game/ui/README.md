### 文件结构

1. src:各种资源文件，如 font,img,voice
2. tools：各种用于 ui 交互的工具
   1. Button:按钮
   2. text: 纯文本
   3. Slider: 拉链
   4. InputBox: 输入栏
   5. component_collection: 需要展示/点击的组件的列表 用于让代码看起来简单点
   6. common:其他工具公用的工具
   7. chessboard: 棋盘
3. windows: 各种窗口
   1. menu: 主菜单界面
   2. sin_player: 单人模式界面
   3. multi_player: 多人模式界面
   4. setting: 设置界面

# 每个窗口中都有一个 main 函数是用于测试的，不是主体逻辑，后面都会删.主体逻辑预计放在 game 的 main 下 2023/9/25 mone
