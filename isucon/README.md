# isucon memo

SSHログイン<br>
（事前にSSH公開/秘密鍵を作成しておりサーバ側で公開鍵を使ってログイン設定している前提）<br>

> https://qiita.com/seigot/items/a6eaebccfd427bb315b4
> PC側で秘密鍵/公開鍵ペア生成する
>```
>$ cd ~/.ssh
>$ ssh-keygen -t rsa -b 4096  # 鍵の名前は適当
>```

```
$ ssh -p xxxxx seigot@xx.xx.xx.xx -i ~/.ssh/seigot_20220xxx
```

## 1.現状の把握

```
１．システム構成の把握（プロセスやファイルの特定）
２．ネットワーク構成の把握（port番号、通信の流れ、etc..）
```

#### サーバーで特定のポート番号を待ち受けているかどうかの確認
> [lsofコマンド入門](https://qiita.com/hypermkt/items/905139168b0bc5c28ef2)

```
$ sudo lsof -P -i:443
```

#### プロセスの確認

[psコマンド　チートシート](https://qiita.com/Higemal/items/6a1f2b4b870d67f67e4e)

```
$ ps -aux
```



## 2.xxx
## 3.xxx

### 各種情報

> https://products.sint.co.jp/topsic/blog/isucon<br> <br>
> Ubuntu 18.04 LTSをベースに、データベースはMySQL、リバースプロキシはnginx、アプリケーションサーバはGoという構成になっています。<br>

> https://isucon.net/archives/56735884.html <br>
> ISUCONについての理解、問題の解き方について深く学ぶことができるオンラインイベント「ISUCON 事前講習 2022 座学」を開催しました。カジュアルに質問を受け付け、参加したことがないという方にも好評をいただきました、ぜひアーカイブをご視聴ください。 

> 過去問の環境構築 <br>
> https://isucon.net/archives/54946542.html

> ISUCON12 予選問題の解説と講評 : ISUCON公式Blog
> https://isucon.net/archives/56850281.html
>> 性能測定→ボトルネック特定→解決、は上手く経験できると面白そう

# 参考

[https://isucon.net/](https://isucon.net/)
[Webサービスチューニングコンテスト ISUCONのススメ](https://www.amazon.co.jp/Web%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%83%81%E3%83%A5%E3%83%BC%E3%83%8B%E3%83%B3%E3%82%B0%E3%82%B3%E3%83%B3%E3%83%86%E3%82%B9%E3%83%88-ISUCON%E3%81%AE%E3%82%B9%E3%82%B9%E3%83%A1-%E6%8A%80%E8%A1%93%E3%81%AE%E6%B3%89%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%EF%BC%88NextPublishing%EF%BC%89-%E4%B8%8B%E7%94%B0-%E9%9B%84%E5%A4%A7/dp/4844379305)
[#isucon で優勝させてもらってきました](https://songmu.jp/riji/archives/2011/08/isucon.html)
