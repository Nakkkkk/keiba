# Description
競馬予想ソフトを自作しました。現在（2021/5/16）は西田式スピード指数を使用しています。

# Expected result!
## ヴィクトリアM(2021/5/16)
```
1st : グランアレグリア&ルメール(99.28)
2nd : マジックキャッスル&戸崎圭(95.59)
3rd : リアアメリア&福永(95.00)
```

# Usage
## Web scraping
```
$ python scraping.py
```
netkeiba.comからseleniumを使用したウェブスクレイピングを行います。
```
$ python get_html.py
```
出力された.txtにレースのURLが書かれているので、htmlディレクトリへリンク先のHTMLをそのままコピーしてきます。
## Preprocessing
```
$ python html2csv.py
```
HTMLに書かれた情報をCSVに変換して、csvディレクトリへ格納します。
```
$ python conv_horse_csv.py
$ python conv_race_csv.py
```
csvディレクトリでCSVデータのトリミングを行います。
## Prediction
```
$ python pred_nishida.py
```
データから予想を行います。

# Note
## スピード指数について
- 今回は、馬とジョッキーそれぞれに対してスピード指数を求め、足して2で割った値を用いて順位を予想しています。
- スピード指数に使用したベースタイムは、「指定の競馬場　かつ　指定の距離　かつ　指定のグラウンド（芝orダートor障害）　かつ　1,2,3勝クラス」といった条件に一致する全レースの平均タイムとしています。
- スピード指数に使用した馬場指数は、「指定の競馬場　かつ　指定の距離　かつ　指定のグラウンド（芝orダートor障害）　かつ　指定の天候」といった条件に一致するデータのみを用いて計算を行っています。データ数が多かろうが少なかろうがとりあえず標準正規分布を仮定して、分布上での「条件下の平均タイム」と「ベースタイム」の差×10を馬場指数として使用しています。データ数が1以下である（分散がゼロになる）場合は、スピード指数を計算していません。
- ジョッキーのスピード指数は、直近200試合のレース結果から算出しています。

# References
- https://zenn.dev/kami/articles/66e400c8a43cd08a5d7f#%E3%83%87%E3%83%BC%E3%82%BF%E3%81%8C%E5%BE%97%E3%82%89%E3%82%8C%E3%81%9F%E3%82%89%E6%95%B4%E5%BD%A2%E3%83%BB%E5%88%86%E6%9E%90%E3%82%92%E3%82%84%E3%81%A3%E3%81%A6%E3%81%84%E3%81%8F
- https://sites.google.com/site/masashikameda/%E3%82%B9%E3%83%94%E3%83%BC%E3%83%89%E6%8C%87%E6%95%B0%E3%81%A8%E5%9F%BA%E6%BA%96%E5%80%A4
- http://www.rightniks.ne.jp/index.php?action=whatspidx_contents&name=sikumi