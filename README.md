`pre-commit`使用, 目前主要用于在提交commit前检查发现项目中的敏感信息，git-hook其他阶段请参考`stages`配置  
# 背景
我司在Github上有众多的开源项目，在版本迭代、代码提交过程中难免有公司相关的敏感信息泄露出去，很容易对公司产生极大的安全风险。<br />尽管安全团队部署有相关Github敏感信息监控扫描工具，发现风险也第一时间跟开发同学反馈并跟进修复，但是这个流程毕竟是事后操作，在我们发现风险的时间点，敏感信息已经被泄露出去，有可能已经被黑客利用。<br />同时根据开发同学反馈，历史的commit记录修改会对版本误伤很大，很容易导致代码和版本混乱，事后的修复工作是相当麻烦的事情。
# 解决方案
那么针对这些问题，有没有可能在开发同学提交commit更新的同时，就能发现其中敏感信息并阻止提方案呢？查找相关资料后，发现[pre-commit](https://pre-commit.com/) 是一个较好的解决方案。
### git hook & pre-commit
Git hooks 是 Git 在事件之前或之后执行的脚本, 用于控制 git 工作的流程。Git hooks 脚本对于在提交代码审查之前识别简单问题很有用。我们在每次提交代码时都会触发这些 hooks，以自动指出代码中的问题，例如缺少分号，尾随空白和调试语句。<br />Git hooks 分为客户端钩子和服务端钩子。客户端钩子由诸如提交和合并这样的操作所调用，而服务器端钩子作用于诸如接收被推送的提交这样的联网操作。<br />pre-commit只是git hook的一部分，pre-commit是属于客户端的。我们这里主要用于在客户端提交commit的阶段触发运行敏感信息工具进行扫描，有敏感信息则阻止提交，整改之后方可通过。
# 安装使用

1. 安装pre-commit ，或者参考官方[pre-commit](https://pre-commit.com/)
```bash
brew install pre-commit
# 或者
pip install pre-commit
```

2. 添加 `pre-commit` 配置

在Git项目根目录下新建`.pre-commit-config.yaml`文件，并写入以下内容
```yaml
repos:
-   repo: https://github.com/thinksec/HunterInfo.git
    rev: v1.0
    hooks:
    -   id: hunter-info
```
这里的repo会从远处获取扫描脚本仓库, 这里给了github和gitee来源, 可以根据自己的网络选择<br>
`https://github.com/thinksec/HunterInfo.git`
`https://gitee.com/thinksec/HunterInfo.git`

3. 安装`git hook` 脚本

在Git项目根目录下执行
```yaml
pre-commit install
```

4. 测试
```bash
PS D:\my_github\PassiveInfoDemo> echo "password=66666" >> demo.txt
PS D:\my_github\PassiveInfoDemo> git add .
PS D:\my_github\PassiveInfoDemo> git commit -m "update"
hunter passive info for commit...........................................Failed
- hook id: hunter-info
- exit code: 1

running: ---------------------------------------- 100% 0:00:00
Please check the scan report in path: 
C:\Users\24543\hunter-info\HunterInfo-2022_10_28_11_36_32.html
1 sensitive information found. can't commit!

```

5. 后续用法

已经完成上述1-3安装步骤后，该Git项目中已经有`.pre-commit-config.yaml`文件，以后只需要在commit的时候按照如下操作即可
```bash
## 在git项目的根目录下
pre-commit autoupdate   # 更新扫描脚本版本
git add .
git commit -m "update"  # commit会自动触发扫描
## 不通过则可以查看扫描报告，复制报告路径到浏览器打开
## 如 C:\Users\24543\hunter-info\HunterInfo-2022_10_24_11_34_47.html
```

# 附录
pre-commit使用的敏感信息扫描工具仓库地址 [[github]](https://github.com/thinksec/HunterInfo) [[gitee]](https://gitee.com/thinksec/HunterInfo)