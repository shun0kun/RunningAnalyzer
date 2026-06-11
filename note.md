# running_analyzer

## Important
- invalidとするときは、swing phaseのmid pointが変化しうることに注意する必要がある。

## Class RunningAnalyzer
- 1stepの抽出アルゴリズム DONE
- 描写メソッド
- vvelの計算 DONE
- 最初と最後のStepは基本捨てるのがいい


## Class Step
- 自分で左右判定する DONE
- enum使うべきか。ただのマクロでよくね。enumはマクロの名前空間？
- Stepの定義をちゃんとする。vgrf_maxがBW以上かどうかとかも見るといいかも。→ "++++++++++0000000000"を1stepとしよう。
- 最初にStepかどうかのvalidateをしてもいい。安全になる。
- vgrf_maxをdataに追加する
- vgrf_max < BWの時は自動でinvalidateする
- invalidate処理をしっかりする。Noneのパラメータが一つでもあればinvalidateにする

## MEMO
- YAGNI
