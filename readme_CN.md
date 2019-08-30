# ppa-mirror

在本地安装debian库非常痛苦，特别是安装源是ppa的库。如果我们能在本地建立一个库，并有一个简单的UI可以进行管理，那这节省了很多时间。

先从一台机器上安装本软件，启动后，在管理界面中同步需要安装的库。注意：为了节省同步时间，输入系统版本和需要安装的具体apt-get后的库名称。然后，我们可以在界面看到同步进度。我们还可以进行对库和源的增删操作。

然后内网服务器可以通过配置一个 IP 为url的source.list来使用我们库了。推荐用ansible进行批量分发。

以后，所有的库名我们都从这台主机上读取了，我们可以方便的管理内网使用的库的版本，快速的进行升级和监控。推荐把阿里云的官方deb也更换为内网的sourcelist以更好的查看库的安装请求。

## deb 打包方式

安装deb其实是对deb打包目录的一种访问。那deb打包是如何进行的呢？
deb的包包含了自动的安装，升级，配置和卸载的方法，是安装应用最简单的方式。一个包通常由源码包和二进制包组成。Debian会指定打包规则，这也是我们所关注的。

## deb repo的URL规范

The sources.list man page specifies this package source format:


   deb uri distribution [component1] [component2] [...]

## deb 服务器（重要）
https://wiki.debian.org/DebianRepository/Format
此链接描述了如果对包进行托管。其实也很简单，托管主要由一个Packages.xz或不同后缀的索引文件和其它文件组成。其中，索引文件会列出一个包的重要信息：而包信息的格式参考：
https://www.debian.org/doc/debian-policy/ch-relationships.html
其中非常重要的是Provides字段，表明了安装这个包时的依赖。