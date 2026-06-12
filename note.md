# running_analyzer

## TODO
- データとる
- 描写メソッド (*****)
- 正規化 (**)
- 平均波形 (*)
- freq (***)

## Important
- invalidとするときは、swing phaseのmid pointが変化しうることに注意する必要がある。
- Stepにvgrf_right, vgrf_leftのいずれかのみ渡す案を考えたが、踏分ができてない時に正しくない値になるため却下。

## Class RunningAnalyzer
- 1stepの抽出アルゴリズム DONE
- 描写メソッド
- vvelの計算 DONE
- 最初と最後のStepは基本捨てるのがいい
- low passやったら解析精度改善する？


## Class Step
- 自分で左右判定する DONE
- enum使うべきか。ただのマクロでよくね。enumはマクロの名前空間？
- Stepの定義をちゃんとする。vgrf_maxがBW以上かどうかとかも見るといいかも。→ "++++++++++0000000000"を1stepとしよう。
- 最初にStepかどうかのvalidateをしてもいい。安全になる。
- vgrf_maxをdataに追加する
- vgrf_max < BWの時は自動でinvalidateする
- invalidate処理をしっかりする。Noneのパラメータが一つでもあればinvalidateにする

## utils
- threshold() → thresholding()。名前どっちがいい？

## 精度の懸念
- Stepの切り取り。Stance phaseで切り取るのもありなのかもしれない。ただ、Stepはstance phaseを含むので、今のところはこのままでいい。
- vvelの計算方法。
- lowpassをかけてないこと。
- どのデータを前方速度とするか。"速度"か"速度計"か。

## MEMO
- YAGNI
