# Inference is Everything: Recasting Semantic Resources into a Unified Evaluation Framework #

This readme describes the dataset introduced in "Inference is Everything: Recasting Semantic Resources into a Unified Evaluation Framework", Aaron Steven White, Pushpendre Rastogi, Kevin Duh, Benjamin Van Durme. IJCNLP, 2017

```
@inproceedings{white2017inference,
	Author = {Aaron Steven White and Pushpendre Rastogi and Kevin Duh and Benjamin Van Durme},
	Booktitle = {IJCNLP},
	Title = {Inference is Everything: Recasting Semantic Resources into a Unified Evaluation Framework},
	Year = {2017}}
```

## Dataset Format ##

This dataset contains three files

1. dpr_data.txt
2. fnplus_data.txt
3. sprl_data.txt

All three files contain empty line separated `entries`. Each `entry` has the following syntax.

> provenance: schema-challenge | FN+ | sprl
> index: {unique string}
> text: {string}
> hypothesis: {string}
> entailed: entailed | not-entailed
> partof: train | dev | test

The `partof` key tells us whether this entry was used as the
train, dev, or test data. The `test` key is the evidence
statement. Given the `test` the `entailed` key tells us
whether the `hypothesis` is `entailed`, or if it `not-entailed`.

The `fnplus_data.txt` also contains an additional key called
the `good_word` which marks the word that was replaced using
the framenet frame annotations.


## Some Statistics ##

The following table shows the number of entries in each file and the labels assigned to them.
```
| Dataset         | Entailed | Not Entailed |
|-----------------+----------+--------------|
| dpr_data.txt    |     1831 |         1831 |
| fnplus_data.txt |    87431 |        67174 |
| sprl_data.txt   |   100806 |        53802 |
```
