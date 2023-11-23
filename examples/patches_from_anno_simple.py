"""
An example of using psimage package to extract patches from image
in accordance with polygonal annotation stored in json file.
Patches can be extracted either in a dence way with fixed stride
or in a random way.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from psimage import PSImage

if __name__ == "__main__":
    patch_s = 100  # size of the patch
    RANDOM_PATCH_LIMIT = 40  # number of random patches extracted from region

    data_path = Path("../data/")
    psim = PSImage(data_path / "msu.psi")
    f = open(data_path / "msu.json")
    for polygon_anno in json.load(f)["objects"]:
        id = polygon_anno["id"]
        print(f"processing polygon {id}...")
        polygon = np.array(polygon_anno["points"]).astype(np.float64)
        # extract patches from region (random way)
        out_path = data_path / f"out/patches_rnd_{id}"
        out_path.mkdir(exist_ok=True, parents=True)
        for i, patch in enumerate(
            psim.patch_gen_random(patch_s, region=polygon)
        ):
            Image.fromarray(patch.data).save(out_path / f"{i+1}.png")
            if i == RANDOM_PATCH_LIMIT:
                break
        # extract patches from region (dense way)
        out_path = data_path / f"out/patches_dense_{id}"
        out_path.mkdir(exist_ok=True, parents=True)
        for i, patch in enumerate(
            psim.patch_gen_dense(patch_s, stride=50, region=polygon)
        ):
            Image.fromarray(patch.data).save(out_path / f"{i+1}.png")

    f.close()
    psim.close()
    print("All patches extracted. That's all.")
