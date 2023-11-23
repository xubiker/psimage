"""
An example of using psimage package to extract patches from
whole slide histological image (PATH-DT-MSU WSS1 dataset)
in accordance with polygonal annotation stored in json file.
Patches can be extracted either in a dence way with fixed stride
or in a random way.
"""

import json
from pathlib import Path

import numpy as np

from psimage import PSImage

if __name__ == "__main__":
    ds_path = Path("../data/")
    out_path_dense = ds_path / "out/patches_wsi_dense"
    out_path_rnd = ds_path / "out/patches_wsi_rnd"
    out_path_dense.mkdir(exist_ok=True, parents=True)
    out_path_rnd.mkdir(exist_ok=True, parents=True)

    psim = PSImage(ds_path / "wsi_lq.psi")
    anno_json = open(ds_path / "wsi_lq.json")

    for k, anno in enumerate(json.load(anno_json)):
        anno_cls = anno["class"]
        anno_polygon = np.array(anno["vertices"], dtype=np.float64)
        print(f"processing region {k + 1} ({anno_cls})")

        # example of random patch extraction from each annotated region
        for i, patch in enumerate(
            psim.patch_gen_random(224, region=anno_polygon, n_patches=100)
        ):
            patch_name = f"{k+1}_{anno_cls}_{i+1}.jpg"
            patch.to_image().save(out_path_dense / patch_name)

        # example of dense patch extraction from each annotated region
        for i, patch in enumerate(
            psim.patch_gen_dense(224, stride=112, region=anno_polygon)
        ):
            patch_name = f"{k+1}_{anno_cls}_{i+1}.jpg"
            patch.to_image().save(out_path_rnd / patch_name)

    print("All patches extracted.")
    anno_json.close()
    psim.close()
