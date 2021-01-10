[First-order-wrapper不是为了制作不道德，非法或不适当的内容。 在这里了解更多。](MANIFESTO.md)

由 LZY 翻译为简体中文。

## Yanderify现在被称为 first-order-wrapper ，以更准确地描述其功能。
由于这个项目已不再处于开发阶段，因此不会到处更改名称。然而，我开始更新我所有项目的文档以使它们更好，因此名称的更改是必要的。您仍然可以将该项目称为Yanderify，所有提到Yanderify的链接都将继续工作。更改 repo 名称会破坏指向此处的任何书签或链接，因此不会发生这种情况。旧文件如下。

# first-order-wrapper
first-order-wrapper 是围绕 [first-order-model](https://github.com/AliaksandrSiarohin/first-order-model) 的包装器。它公开了一个简单的用户界面，设计成任何人都可以使用，任何技术水平。 first-order-model 以前很难被普通人使用，因为它需要命令行和库的安装知识。Yanderify通过提供一个完整的环境消除了这些问题，并将所有必要的组件捆绑在其中。

有关最新版本，请参见“版本”选项卡。回购不一定是最新的。但是，[latest-v4 分支](https://github.com/dunnousername/yanderifier/tree/latest-v4)包含了本文撰写时的最新代码，而master则包含了后面两个主要版本的代码。

## 它能做什么

下面是first-order-model可以做什么的一个例子；这个图像是由 [First Order Motion Model论文的作者创建的，并且是从他们的存储库中获取的。](https://github.com/AliaksandrSiarohin/first-order-model)Yanderify的大部分繁重工作都是由这些论文作者编写的代码完成的，因此如果您感兴趣，我建议您去查看他们的存储库。

![例子（在中国大陆可能无法显示）](https://github.com/AliaksandrSiarohin/first-order-model/raw/master/sup-mat/relative-demo.gif)

## 工作原理

双击 `yanderify.exe` yanderify.exe将弹出一个看起来像这样的窗口：
![程序截图（在中国大陆可能无法显示）](readme_mats/ss1.png)

- “我没有 >=GTX750 的NVIDIA显卡”：选中此选项将启用CPU模式，这会慢很多，但对于没有兼容图形卡的用户来说，这是唯一的方法。
- “选择视频”：单击此将显示文件选择框。 该文件应该是您想要为新面孔设置动画的视频； 换句话说，该视频将“驱动”图像以相同的方式移动。
- “选择图像”：这是要设置动画的人脸的裁剪图片。换句话说，这就是视频“穿”的脸。
- “选择输出”：这是存储结果的位置。

只需点击“开始”，您的视频就会重新设置动画，并用源音频重新编码！

## 附录

加入我们的 [discord服务器（在中国大陆可能无法访问）](https://discord.gg/eEvTzRP) (已更新)
很多人都要求我发Twitter。 我可能不会非常活跃，但是在这里：@dunnousername2（在中国大陆可能无法访问）
