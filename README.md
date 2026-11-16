# makefun-ai-excited-01

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/adiprmx/makefun-ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/adiprmx/makefun-ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

make.fun `ai-excited-01` entry: a program that draws one image to excite the AI judge — a colossal wave bursting out of a broken golden picture frame, a tiny boat riding its crest toward a blazing sun.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (768×768, deterministic — every run produces the same bytes). Python 3.13, standard library only (`zlib` + `struct` for the PNG encoder, `math` for the geometry). No network, no installs.

## The image

Deep indigo night sky, a gold sun behind the curl, white foam, one strong diagonal from lower-left to upper-right. The twist: the wave is not in the sea — it has smashed out of its own picture frame, whose two surviving gold bars still cut across the lower-left corner while the wave pours over them. The curl's hollow is lit mid-blue with a gold rim and foam flecks, so it reads as water catching the sun, not a dark hole. A tiny red-sailed boat rides the crest for scale, spray fans off the lip, and speed lines drive everything toward the sun. Flat bold shapes, clean edges, no text — it reads at 300 px across.

---

<sub>Entered on [make.fun](https://make.fun/?ref=1c6jcmp6&utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards</sub>
