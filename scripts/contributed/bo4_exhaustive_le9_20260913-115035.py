"""BO4: exhaustive enumeration of EVERY string of 1 to 9 characters over [a-z0-9_] (37^9 = 1.3e14
candidates, ~40 min on an RTX 3090 with a 2^28-bit bitmap prefilter), exact-id matched against the
open ids of every non-worthless pocket. Provable closure: no BO4 asset name of nine characters or
fewer over that alphabet remains unknown. Expected chance matches at this size: 1.4.
Kernel: bo4_tokfind_gpu.cu with an empty prefix and an empty suffix."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_exhaustive_le9.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
