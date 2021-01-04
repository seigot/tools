# Usage

`README.md`の英単語チェック用

```
cd .
find . -name README.md > flist.log
python3 check_spell.py
```

該当の`README.md`を探す用

```
find . -name README.md | xargs grep -rn "recieps" *
```
