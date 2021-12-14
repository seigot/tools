## usb ssd に tetris環境構築できるかどうかのトライアル用

作成中... 

## 事前準備

- 作業用のPCを用意する（Mac/Windows）
- usb ssd を入手する（Ubuntuをインストールする用）  
(例)
> [バッファロー SSD 外付け 250GB 超小型 コンパクト ポータブル PS5/PS4対応(メーカー動作確認済) USB3.2Gen1 ブラック SSD-PUT250U3-B/N](https://www.amazon.co.jp/gp/product/B08N4F3CVY/ref=ppx_yo_dt_b_asin_title_o02_s01?ie=UTF8&psc=1)  

- usb メモリ を入手する（Ubuntuのインストーラを書き込む用、16GB以上あればOK）  
(例)
> [バッファロー【国内メーカー】 USBメモリ 16GB USB3.2(Gen1)/3.1(Gen 1)/3.0/2.0 充実サポート RUF3-K16GA-WH/N【Amazon.co.jp限定】](https://www.amazon.co.jp/gp/product/B087CHWZ33/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1)  

- ubuntu OSインストーラを取得
> [Ubuntu20.04LTSのブートUSBをMacで作成する](https://qiita.com/seigot/items/faea0998e17c40b3a63e)

## ゴール
usb ssd に Ubuntuをインストールする（+tetris環境を起動する）

- tetris環境
> https://github.com/seigot/tetris

## ubuntuのインストーラを準備する

### ダウンロード

以下からOSイメージ（ubuntu-20.04-desktop-amd64.iso）をダウンロードして作業用のPCに保存する。  

[日本国内のダウンロードサイト](https://www.ubuntulinux.jp/ubuntu/mirrors)  
→Ubuntuのリリースイメージから、http://で始まるミラーサイトへアクセス  
※ Ubuntuのパッケージアーカイブミラーではなくリリースイメージから選ぶ  
→Ubuntu 20.04 LTS (Focal Fossa)  
→64-bit PC (AMD64) desktop image  

### Ubuntuのインストーラを書き込む用のusb メモリにOSイメージを書き込む

以下のツールを利用する  

> [Ethcer](https://www.balena.io/etcher/)を使い、  
> ダウンロードしたOSイメージ（ubuntu-20.04-desktop-amd64.iso）を書き込む

--> Flash from file: ubuntu
    Select target  : USBメモリ

## usb ssd へubuntu環境をインストールする

windowsの場合

起動直後にF2ボタン（or F何かのボタン）を押す？
--> BIOS画面に遷移して、USBメモリから起動する設定をする

## usb ssd からubuntuを起動する

起動直後にF2ボタン（or F何かのボタン）を押す？
--> BIOS画面に遷移して、usb ssd から起動する設定をする

## tetrisを動かす

terminalから以下を実行する

```
git clone https://github.com/seigot/tetris
cd tetris
bash start.sh
```

## Disk I/O の確認

`/dev/sda`の例

```
$ sudo fdisk -l
ディスク /dev/sda: 238.49 GiB, 256060514304 バイト, 500118192 セクタ
...
デバイス   開始位置  最後から    セクタ サイズ タイプ
/dev/sda1     65535    983024    917490   448M EFI システム
/dev/sda2    983025  16580354  15597330   7.4G Linux スワップ
/dev/sda3  16580355 500097584 483517230 230.6G Linux ファイルシステム
```

`Timing buffered disk reads`が`100MB/sec`を超えていればとりあえずよし？

```
$ sudo hdparm -tT /dev/sda
/dev/sda:
 Timing cached reads: 39954 MB in  1.98 seconds = 20131.94 MB/sec
 Timing buffered disk reads: 1020 MB in  3.04 seconds = 335.62 MB/sec
```

## 参考
[Ubuntu 20.04 LTS インストール方法（外付けドライブ用）](https://qiita.com/koba-jon/items/019a3b4eac4f60ca89c9)  
[Ubuntu20.04LTSのブートUSBをMacで作成する](https://qiita.com/seigot/items/faea0998e17c40b3a63e)  
[HDDのパーティションを完全削除する方法](https://qiita.com/ricrowl/items/4cc3aa1727a08c8d8413)  
