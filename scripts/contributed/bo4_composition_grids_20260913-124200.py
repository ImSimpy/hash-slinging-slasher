"""BO4 pockets whose names are compositions of OTHER pockets' names, all of which are already
plaintext: attachment_unique = au_<weapon base>_<attachment> (883 of 1,987 open in one pass),
weapon_camo = camo_t8_<weapon base> (39 of 44), player_outfit = po_c_t8_<mode>_spe_<specialist>_<outfit>
(15). Weapon bases are the 1,142 weapon names with mode/_t8/_upgraded suffixes stripped;
attachments are the 331 attachment names plus the leading token of every weapon name.
Measured zeros: tagfx (104 gadget tokens x 23 forms, 0 of 117) and light_description
(gfx_dlight_<type>_<shape>_r<N> grid, 0 of 1,472) do not follow a composition rule.
Generator: C:/tmp/bo4_vox/compose.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(here, "bo4_composition_grids.txt"), encoding="utf-8"):
    if l.strip(): print(l.strip())
