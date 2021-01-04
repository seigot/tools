# Usage

> [指定したURLのリンクが有効かどうかをチェックするpythonスクリプトを作成](https://qiita.com/seigot/items/534ca3089d217200a1d6)<br>
<br>
URLチェック用


#### チェック対象のURLリスト作成

```
grep -r "https://" * > test.txt
cat test.txt | sed -e 's/.*https//' | sed "s/^/http/g"  > test.txt
cat test2.txt | sed 's/>//g' | sed 's/"//g' | sed 's/)//g' | sed 's/;//g' | sed 's/]//g' | cut -d' ' -f 1 > input.txt 
```

#### チェック

```
python3 check_url.py
```

結果OK/NGを以下に出力する

```
emacs out.txt
```
