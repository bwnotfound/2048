### 文件结构
1. src:各种资源文件，如font,img,voice
2. tools：各种用于ui交互的工具
    2023.9.19:我在menu界面将目前的四个tools展示了一遍，在根目录from game.ui.windows.menu import main后执行main()可查看执行效果(mone)
    1. button:按钮                 
    2. text: 纯文本               
    3. zipper: 拉链
    4. input_box: 输入栏
    5. need_to_show: 需要展示的组件的列表 用于让代码看起来简单点
3. windows: 各种窗口
    1. menu: 主菜单界面
    2. sin_player: 单人模式界面
    3. multi_player: 多人模式界面
    4. setting: 设置界面
