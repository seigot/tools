
以前からやりたいと言っていたパラメータ自動評価環境メモ

```
step1. 誰かのaichallenge2023リポジトリをgit cloneする
step2. AWSIM/autowareをビルドして実行×10回くらい
step3. step2実行時の評価結果をどこかに記録する
```

のうち、step2/step3 の部分を作成してみたもの（実体はシェルスクリプト）   
よかったら実行してみて下さいー、これで数十回の連続実行が楽になるはずです。

リポジトリURL  
https://github.com/seigot/tools/tree/master/aichallenge_2023

```
autorun.sh
stop.sh
```

#### 実行方法

前提条件
- README.mdに沿って事前準備完了していること
- 各種インストールが完了していること
- 地図データ(pcd,osm)のコピーが完了していること
- autowareのサンプルコードの手動実行が確認できていること

コマンド

```
cd ${HOME}/aichallenge2023-sim
wget https://raw.githubusercontent.com/seigot/tools/master/aichallenge_2023/autorun.sh
wget https://raw.githubusercontent.com/seigot/tools/master/aichallenge_2023/stop.sh
bash autorun.sh #二回目以降はここだけ実行

bash autorun.sh -l 3 -s 200    # LOOP(-l)回数指定したい場合や、完了待ちsleep時間（-s）指定したい場合はoption指定すればOK
```

結果(`result.json`)は以下のようになる

```
~/aichallenge2023-sim$ cat result.json 
Time	rawDistanceSocre	distanceScore	task3Duration	isOutsideLane	isTimeout	hasCollided	hasExceededSpeedLimit	hasFinishedTask1	hasFinishedTask2	hasFinishedTask3
20230806101014_seigot_main	33.3776	31.7087	3.20045	false	false	true	false	false	true	false
20230806101355_seigot_main	33.5419	31.8648	3.19995	false	false	true	false	false	true	false
20230806101737_seigot_main	33.4703	31.7968	3.19987	false	false	true	false	false	true	false
20230806102119_seigot_main	33.5021	31.827	3.19994	false	false	true	false	false	true	false
20230806102500_seigot_main	33.5126	31.837	3.1991	false	false	true	false	false	true	false
20230806102842_seigot_main	33.3896	31.7201	3.20017	false	false	true	false	false	true	false
20230806103224_seigot_main	33.4781	31.8042	3.19981	false	false	true	false	false	true	false
20230806103605_seigot_main	33.5385	31.8616	3.19992	false	false	true	false	false	true	false
20230806103947_seigot_main	33.5385	31.8616	3.19992	false	false	true	false	false	true	false
20230806104329_seigot_main	33.5927	31.9131	3.39991	false	false	true	false	false	true	false
...
```

`distanceScore`が伸びるようにパラメータ調整や各種工夫に励めばOK
