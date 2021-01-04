# Usage

> [pythonで英語スペルミスの検出を試みた](https://qiita.com/seigot/items/3b29b4d03297c4275bb1)<br>
<br>
`README.md`の英単語チェック用

```
cd .
find . -name README.md > flist.log
python3 check_spell.py
```

結果Falseの英単語を以下に出力する

```
emacs file.txt
```

該当の`README.md`を探す用

```
find . -name README.md | xargs grep -rn "recieps" *
```
