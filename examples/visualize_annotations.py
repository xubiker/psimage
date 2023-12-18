"""
An example of generating image previews from dataset with
drawn polygonal annotations.
"""

from pathlib import Path

from psimage import PSImage
from psimage.base.anno_visualizer import AnnoDescription

if __name__ == "__main__":
    # Define path to the dataset, e.g. PATH-DT-MSU.
    ds_path = Path("/Users/xubiker/dev/PATH-DT-MSU_WSS1_psi/")

    # Define output path for previews.
    out_path = Path("/Users/xubiker/dev/PATH-DT-MSU_WSS1_psi_previews/")
    out_path.mkdir(parents=True, exist_ok=True)

    # Pretend that we do not know the annotation classes. For this case
    # we can cal AnnoDescription.auto_from_files() method that automatically
    # extract all the annotation classes info from the json files and
    # create AnnoDescription object from it. All colors will be chosen
    # automatically and will be distinct.
    anno_dsc = AnnoDescription.auto_from_files(ds_path)

    # Iterate over all psi files in the dataset folder and generate
    # a preview with annotations for each one. Save the preview in the
    # output folder. Limit all previews size to 4000 pixels by side.
    for f in ds_path.iterdir():
        if f.is_file() and f.suffix == ".psi":
            print(f"Visualizing image {f.name}...")
            psim = PSImage(f)
            img = psim.annotations_preview(
                annotations=ds_path / f"{f.stem}_anno.json",
                max_side=4000,
                anno_description=anno_dsc,
            )
            img.save(out_path / f"{f.stem}.jpg")
            psim.close()
