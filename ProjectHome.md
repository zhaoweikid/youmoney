A simple personal finance software for you. Support Windows, Linux, MacOS X.

Source depend:<br>
<li> python 2.5 + </li>
<li> wxPython 2.8.9 + </li>
<li> python sqlite3 module </li>
<br>
YouMoney（有钱记账）是一个跨平台的免费个人记账软件。它可以运行在windows, linux, macos x。他使用简单，只有记账的核心功能。作者认为simple is better，简单够用就好。不需要大而全的东西。界面支持英文，简体中文，繁体中文和日文。<br />
功能包括：<br>
<li>支持分类。收入和支出条目都属于某个分类。</li>
<li>可以对每个分类统计支出和收入情况</li>
<li>支持循环记录。即可以为固定支出，按每月，每周，每日，周末，工作日自动添加支出或者收入</li>
<li>可以统计每个月或者年的支出、收入、结余情况</li><br />


<h1>下载链接</h1>

<blockquote><h2>源代码</h2>
<blockquote>源代码: YouMoney-src-0.9.5.zip    <a href='http://youmoney.googlecode.com/files/YouMoney-src-0.9.5.zip '>点击下载</a></blockquote></blockquote>

<blockquote><h2>Windows</h2>
<blockquote>Windows安装包: YouMoney-0.9.5.exe    <a href='http://youmoney.googlecode.com/files/YouMoney-0.9.5.exe'>点击下载</a><br />
Windows绿色非安装版: YouMoney-noinstall-0.9.5.zip    <a href='http://youmoney.googlecode.com/files/YouMoney-noinstall-0.9.5.zip'>点击下载</a><br /><br />
Vista和Windows 7用户，建议下载绿色非安装版。</blockquote></blockquote>

<blockquote><h2>Linux</h2>
<blockquote>Linux RPM包(Fedora): YouMoney-0.9.5-1.i586.rpm    <a href='http://youmoney.googlecode.com/files/YouMoney-0.9.5-1.i586.rpm'>点击下载</a><br />
Linux DEB包(Ubuntu): youmoney_0.9.5-1_all.deb     <a href='http://youmoney.googlecode.com/files/youmoney_0.9.5-1_all.deb'>点击下载</a><br /><br />
注意：从0.6.6版本开始修改了数据文件路径，从存放在YouMoney目录下的data目录中改为存放到用户目录下的.youmoney目录中。所以0.6.5及以前版本升级注意拷贝YouMoney目录中的data目录下的内容到用户目录下的.youmoney里。</blockquote></blockquote>

<blockquote><h2>Mac OS X</h2>
<blockquote>Mac OS X 10.5以上 dmg包: YouMoney-macosx10.5-0.9.5.dmg.zip    <a href='http://youmoney.googlecode.com/files/YouMoney-macosx10.5-0.9.5.dmg.zip'>点击下载</a>
<br />
<b>注意：windows版本，数据默认存放在YouMoney目录里面的data目录中，linux，mac os x的数据默认存在在用户目录下的.youmoney目录中。因此，升级时，windows安装版只需要覆盖安装，windows非安装版注意拷贝data目录到新版中。linux，mac os x升级不用管数据问题。</b></blockquote></blockquote>

截图：Windows XP<br>
<br>
<img src='http://life.chinaunix.net/bbsfile/month_1007/10070516454e92d15d4ed500c8.png' />

截图：Ubuntu 9.10<br>
<br>
<img src='http://life.chinaunix.net/bbsfile/month_1007/10070516454ae725884e257dc4.png' />

截图：MacOS X 10.5.8<br>
<br>
<img src='http://life.chinaunix.net/bbsfile/month_1007/1007051645599affc1d12ca65a.png' />


版本更新：<br>
<br>
2010-06-07    <b>0.9.5</b> <br>
<li>修改统计饼图一些情况下有空白的bug</li>
<li>解决在linux下，添加对话框不能关闭的问题</li>
<li>解决ubuntu10.04等linux系统下，主窗口不能关闭，需要强行结束的问题</li>
<li>增加繁体中文支持</li>

2010-05-07    <b>0.9.2</b> <br>
<li>分类页增加显示当天收入，支出</li>
<li>分类页增加显示结余</li>
<li>分类统计中增加显示结余</li>
<li>月统计中的柱状图，修改为同时显示收入，支出，结余</li>
<li>增加表格统计，以表格方式显示某时间段的收入，支出，结余</li>
<li>解决分类统计数据跨年可能不准确的问题</li>



2010-04-25    <b>0.8.8</b> <br>
<li>解决ilorn.mc提出的，设置了密码后，密码不能删除的问题。</li>
<li>增加canlynet提出的收入和支出列表可以点击标题栏排序</li>
<li>修改收入，支出，循环记录列表中分类显示的方式，改为显示“一级分类->二级分类”</li>
<li>解决当不同一级分类下有同名的二级分类时，可能会有统计数据错误的问题</li>
<li>分类列表增加“今日总计”显示今天的支出，收入信息</li>


2010-04-15    <b>0.8.7</b> <br>
<li>解决自动更新时，windows版本删除了原有数据的问题。<font color='red'>原有数据可以从安装目录下的tmp/backup/data中找回</font>。</li>


2010-04-15    <b>0.8.6</b> <br>
<li>解决在删除分类时，如果该分类有循环记录时，会造成程序无法打开的问题。</li>
<li>更新一些日文翻译。</li>

2010-03-29    <b>0.8.5</b> <br>
<li>解决统计饼图，在某些分类数据很小的时候，可能会出现画图错误的问题。</li>

2010-03-28    <b>0.8.4</b> <br>
<li>解决windows版安装版，有可能在卸载程序时，误删安装在当前用户下的“开始”“程序”中的其他程序的快捷方式的问题。</li>

2010-03-28    <b>0.8.3</b> <br>
<li>解决YouMoney运行在带有空格的路径下不能自动更新的问题。</li>

2010-03-26    <b>0.8.2</b> <br>
<li>解决循环记录，在收入或支出中删除当天自动循环的记录，还会自动添加的问题。</li>
<li>修改循环记录，在第一次刚添加每周或每月的循环记录时，马上添加一个，而不是等到下周一或者下个月1号</li>
<li>增加自动升级功能。rpm，deb和dmg安装的版本不支持。“关于”菜单下增加升级选项。</li>
<li>根据qd.freebsd的建议，在添加支出或者收入金额时，可以输入.xx表示0.xx。</li>
<li>根据shuge.lee的建议，增加菜单快捷键。</li>
<li>修改shuge.lee提供的bug：在添加支出、或收入时，下拉框中的选项，如果做了手工编辑，会保存失败的问题。改为不可编辑。</li>
<li>解决内部计算md5sum，在windows上和linux上结果不一致的问题。</li>
<li>修改升级文件格式</li>
<li>右键弹出菜单增加编辑选项。编辑对话框的标题修改带“编辑”字样</li>

2010-03-23    <b>0.8.1</b> <br>
<li>增加自动循环记录。可以按一定周期自动增加收入或者支出。</li>


2010-03-17    <b>0.6.6</b> <br>
<li>修改菜单栏。没有新建数据库，改为新建账户</li>
<li>增加更改账户路径</li>
<li>解决删除默认账户数据文件，有可能造成YouMoney不能启动的问题</li>
<li>自动更新时传递更多的数据</li>
<li>解决创建新账户不会导入默认分类的问题</li>
<li>在非windows平台，更改默认的账户数据文件到用户目录下的.youmoney目录中</li>
<li>增加发布针对linux平台的rpm包和deb包，以及苹果系统的dmg。</li>
<li>解决刚打开YouMoney，感觉窗口会跳动一下的问题。</li>

2010-03-04    <b>0.6.5</b> <br>
<li>解决编辑菜单下，编辑支出误写为编辑收入的问题</li>
<li>解决YouMoney不能运行在中文路径下的问题</li>
<li>解决添加收入时，选择不关闭对话框，继续添加无效的问题</li>

2010-03-01    <b>0.6.4</b> <br>
<li>增加默认分类</li>
<li>显示分类时，修改为只展开主类。</li>

2010-02-28    <b>0.6.3</b> <br>
<li>修改csv格式导入导出功能，导入数据时有进度条</li>

2010-02-26    <b>0.6.2</b> <br>
<li>修改自动更新版本识别在一些情况下版本判断错误的问题</li>
<li>增加csv格式导入导出功能</li>

2010-02-22    <b>0.6.1</b> <br>
<li>增加设置密码功能，如果设置了密码，运行YouMoney时，会提示输入密码</li>

2010-02-19    <b>0.5.4</b> <br>
<li>增加自动检查新版本并提示的功能</li>
<li>按照jaypei97159的建议，修改setup.py，把一些lib打包到exe中</li>
<li>根据bobby.zeng的建议，增加快捷键。以及添加收入和支出时对话框可以选择不关闭继续使用。谢谢bobby.zeng提供的代码。</li>

2010-02-17    <b>0.5.3</b> <br>
<li>修改统计时，选择“结余”时，分类显示错误的问题</li>
<li>修改结余统计时，如果结余为负值，显示错误的问题</li>
<li>修改数据库路径提示条件为只有在windows系统盘默认路径才会提示</li>

2010-02-16    <b>0.5.2</b> <br>
<li>修改统计图显示的一些bug</li>

2010-02-12    <b>0.5.1</b> <br>
<li>根据a.roolce的建议，修改统计方式，改为饼图和柱状图显示</li>

2010-01-15    <b>0.3.11</b> <br>
<li>增加日文支持。感谢JackyMa提供</li>

2010-01-12    <b>0.3.10</b> <br>
<li>修正xiao li提出的，添加收入/支出条目时，金额写“100元”会报错的问题</li>
<li>修正数据库插入时，一些特殊字符可能会报错的问题</li>
<li>修正JackyMa提出的，日文系统上无法运行的问题</li>

2010-01-11    <b>0.3.9</b> <br>
<li>修正新安装的情况下，有可能data目录没有创建造成无法启动</li>

2010-01-10    <b>0.3.8</b> <br>
<li>修正在MacOS X 10.5.8 下的一些错误</li>
