`pre-commit`使用, 目前主要用于在提交commit前检查发现项目中的敏感信息，git-hook其他阶段请参考`stages`配置  
在git项目中

### 用法
#### 安装pre-commit
```
brew install pre-commit
# 或者
pip install pre-commit
```

```
repos:
-   repo: https://github.com/thinksec/HunterInfo
    rev: v1.0
    hooks:
    -   id: hunter-info
```