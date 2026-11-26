# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/zurrrtzy-create/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/zurrrtzy-create/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A newspaper front page summing up the world news of Thursday 26 November
2026: 30 stories, from the Houthi claim on Saudi Arabia's Ras Tanura
refinery and two tankers hitting Iranian mines in the Strait of Hormuz
(Brent at $94.71, the US telling its citizens to leave Iran at once) to
Washington proposing tariffs on 14 trading partners (China faces an extra
20%) and the FCC clearing SpaceX's "Starmind" — up to one million
satellites as AI data centres in orbit; plus Kim Jong Un's wider tactical
nuclear deployment, the Bogor mine flood that killed 13, the EU leaders'
clash over a €45bn Ukraine loan, Spain's snap election, Nvidia sliding
3.9%, Australia's Digital Duty of Care Act, and 15 more stories — with a
date check box that honestly notes what was left out (the Chen Jining
probe and the Raytheon contract are from Tue 24 Nov, and the tariff
proposal, SpaceX approval, Iran alert, tech law, Luma ruling, Champions
League matches and Rams–Packers game are from Wed 25 Nov).

`main.py` (Python 3.13, standard library only) copies `entry.png` to
`/output/entry.png` (1024x1024, deterministic - two runs write identical
bytes). The image itself was rendered by `render.py` (Pillow + the real
EB Garamond and Playfair Display fonts in `fonts/`, SIL OFL). No network,
no randomness, no wall-clock time.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
