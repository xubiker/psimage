# psimage

PSImage is a python package to work with images in `psi` format, that is used in *pathscribe* software.

## Installation

Download wheels distro from the [releases section](https://github.com/xubiker/psimage/releases), then install it:

```bash
pip install psimage-0.2.0-py3-none-any.whl
```

**The minimal required version of python is 3.10.**

## Data

Sample images in `psi` format are provided in a [data](./data/) folder of this repository.

PATH-DT-MSU WSS1 (v1), WSS2 (v1) datasets in `psi` format with polygonal annotations in `json` format are available at `sinope` server `/home/data_repository/PATH-DT-MSU_dev/` and also at yandex disk: [WSS1](https://disk.yandex.ru/d/2jmKiLED22aHSw), [WSS2](https://disk.yandex.ru/d/5oW4Ezo5c9PbOQ).

## Usage

### Open image

You can work with locally stored images in `psi` format and either use with clause:

```python
from pathlib import Path
from psimage import PSImage
p = Path("./data/wsi_lq.psi")
with PSImage(p) as psim:
    ...
```

or you can manually open and close image:

```python
from pathlib import Path
from psimage import PSImage
p = Path("./data/wsi_lq.psi")
psim = PSImage(p)
...
psim.close()
```

### Get general image properties and previews

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/wsi_lq.psi")
with PSImage(p) as psim:
    # -- get width, height, magnification, tile size
    print(f"Image {psim.height} x {psim.width} at {psim.magnification}x")
    # -- get size of a tile and number of tiles
    print(f"tile size: {psim.tile_size}, number of tiles: {psim.n_tiles}")
    # -- get codec and level of quality (1-100)
    print(psim.codec, psim.quality)
    # -- get available previews for PSImage
    print("Previews:")
    for preview_name, preview_img in psim.previews.items():
        print(f"preview {preview_name}: {preview_img.width}x{preview_img.height}")
        preview_img.show()

```

### Work with layout and individual tiles

In `psi` format the image is stored as a pyramid of tiles. The layers of the pyramid are numbered by powers of two (1, 2, 4, 8, 16, ...). The resolution of each superior layer is 2 times smaller. Each layer consists of tiles. The top layer of the pyramid consists of only one tile. Almost all tiles (except last row and last column) are small images of `tile_size` size.
To work with pyramid structure there is a `TilesLayout` class.

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/wsi_lq.psi")
with PSImage(p) as psim:
    # -- get resolution of each layer
    print()
    for layer in psim.layout.layers:
        size = psim.layer_size(layer)
        print(f"layer {layer}, image size: {size}")
```

```bash
layer 1, image size: (28749, 37848)
layer 2, image size: (14374, 18924)
layer 4, image size: (7187, 9462)
layer 8, image size: (3593, 4731)
layer 16, image size: (1796, 2365)
layer 32, image size: (898, 1182)
layer 64, image size: (449, 591)
layer 128, image size: (224, 295)
```

Each tile in the pyramid is specified by `TileDescriptor` class. It contains the coordinates of the tile: `z` corresponds to layer index, `y, x` correspond to the position of the tile inside layer.

You can get all tile descriptors for the image or get them grouped by layers or get tile descriptors for the specific layer.

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/wsi_lq.psi")
with PSImage(p) as psim:
    # -- get all tile descriptors
    print(f"Tiles: {psim.layout.tiles_all()[:3]}...")

    # -- get all tile descriptors grouped by layer
    print()
    for layer, tiles in psim.layout.tiles_per_layer().items():
        print(f"Layer {layer}, tiles: {len(tiles)} ({tiles[:3]}...)")

    # -- get all tiles descriptors for certain layer
    print()
    tiles = psim.layout.tiles_at_layer(4)
    print(tiles[:3])

```

To get the tile content as *numpy array* or *PIL Image* object using tile descriptor you can either call method `get_tile` and pass `z, y, x` coordinates of the tile to it or call `get_tile_by_code` method and pass descriptor's code to it or call `get_tile_by_dsc` and pass the descriptor.

```python
from pathlib import Path
from PIL import Image
from psimage import PSImage

p = Path("./data/wsi_lq.psi")
with PSImage(p) as psim:
    tiles = psim.layout.tiles_at_layer(4)
    tile_dsc = tiles[int(len(tiles) // 2)]

    # -- access tile by coordinates
    tile_arr = psim.get_tile(tile_dsc.z, tile_dsc.pos_y, tile_dsc.pos_x)
    print(tile_arr.shape, tile_arr.dtype)
    tile_img = Image.fromarray(tile_arr)
    tile_img.show()

    # -- access tile by code
    tile_img = psim.get_tile_by_code(tile_dsc.code)

    # -- access tile by descriptor
    tile_img = psim.get_tile_by_dsc(tile_dsc)

```

### Extract arbitary regions from `psi` image

There are 2 ways to access arbitary regions of the image.

Firstly you can call `get_region` and pass the TL and BR coordinates (in terms of layer 1 resolution) of the desired rectangle and the target resolution of the desired region. In this way the best layer for extraction is choosen automatically depending on the specified sizes.

Secondly you can call `get_region_from_layer` and pass the index of the layer (1, 2, 4, 8, ...) and the TL and BR coordinates of the rectangle region.

Both methods return *numpy array* object.

```python
from pathlib import Path
from PIL import Image
from psimage import PSImage

p = Path("./data/wsi_lq.psi")
with PSImage(p) as psim:
    # -- extract region (choose the best layer automatically)
    roi = psim.get_region((10000, 10000), (15000, 16000), (400, 500))
    Image.fromarray(roi).show()

    # -- extract some region from certain layer
    roi = psim.get_region_from_layer(64, (100, 150), (250, 250))
    Image.fromarray(roi).show()
```

### Export from `psi` format

You can export all tiles of an image to a given folder using `export_tiles` method.
Or you can export a downscaled version of the image using `export_simple` method. In this case you either pass the downscale factor or the maximum size of the image (considered on the larger side). This method also have `auto_downscale` parameter, that if true automatically downscales the image to the allowed limit if it is too big.

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/wsi_lq.psi")
with PSImage(p) as psim:
    # -- export all tiles of psimage into a folder as separate images
    # -- (n_procs param is used for multiprocessing)
    psim.export_tiles(Path("../data/out/wsi_lq_tiles"))

    # -- specify scale or desired resolution
    psim.export_simple(Path("../data/out/export_1.jpg"), scale=0.1)
    psim.export_simple(Path("../data/out/export_2.jpg"), max_side=2000)

```

Simular to `export_simple` method there are `to_array` and `to_image` methods that take 3 optional params (`scale`, `max_side`, `auto_downscale`) and return the PIL Image object or an numpy array. If `auto_downscale=False` and the traget size (downscaled size that is defined by `scale` or `max_side` or source size if both `scale=None` and `max_side=None`) exceeds the psimage limit an exception is thrown.  

### Extracting patches

Many methods of processing and analysis of big images and especially WSIs are working with small image fragments  called patches. This package allows to extract patches from images in `psi` format.

#### Extract patches from the whole image

To extract patches from WSI without any annotations you can use `patch_gen_random` and `patch_gen_dense` methods, which provide generators that extract patches either randomly or densly from WSI. You shold specify the patch size, layer to extract patches from and stride (in case of dense extraction).

In case of `patch_gen_random` you can specify the `n_patches` parameter to stop generator after a certain number of iterations.

#### Extract patches in accordance with polygonal annotation

The easiest way to annotate big images (e.g. WSIs) is to use polygonal markups. They are usually stored in `json` files as lists of vertices with some additional information (class label, tags, descriptions, etc).

This package allows to extract patches from `psi` image that are located inside polygon, which is defined as a numpy array of vertices.

This can be done in two ways:

1. by extracting random patches within polygon (`patch_gen_random` method with `region` argument). In this case the generator is infinite.
2. by extracting patches densly within polygon (`patch_gen_dense` method with `region` argument). In this case the generator will stop producing patches after covering the polygon.

In case of `patch_gen_random` you can specify the `n_patches` parameter to stop generator after a certain number of iterations.

When extracting patches according to polygons you can also specify the `region_intersection` parameter, which sets the area treshold for "accepting the patch to be inside polygon".

Examples of extracting patches with polygonal annotations are provided in [patches_from_anno_simple.py](./examples/patches_from_anno_simple.py) and [patches_from_anno_wsi.py](./examples//patches_from_anno_wsi.py) scripts. In case of WSI the json annotation from PATH-DT-MSU dataset is used.

### Visualization of annotations

Psimage package allows to perform visualization of polygonal annotations of `psi` iamges. Since images `psi` can be of very high resolution the visualization is performed for a downscaled image and is called an *annotation preview*.

Each object of annotation is defined as a string label and a list of coordinates pairs, that form a polygon.

In order to create a visualization call `annotations_preview` method of `PSImage`. This method has several params:

1. `annotations` - either a path to json file with annotations or an iterable of tuples of label and numpy array of vertices.
2. `scale`, `max_side`, `auto_downscale` params that control downscale. Simular to the ones in  `to_array`, `to_image`, `export_simple` methods.
3. `anno_description` - optional parameter of `AnnoDescription` object storing the description of annotation, that includes classes and colors. If `anno_description=None` description will be built automatically.
4. `vis_params` - optional parameter of `AnnoVisualizerParams` object controlling the visualization (line width, legend location, fill the polygons or not, with what transperrency).

`AnnoDescription` class is capable for storing labels, descriptions, alternate labels and colors. If you need, you can set it up manually by yourself. But it also can be constructed automatically for the existing dataset. In this case all `json` files in the dataset will be analyzed, a set of labels will be extracted, for each label a distinct color will be chosen. To do it just call `auto_from_files` class method and pass the path to the dataset (or a single `json` file):

```python
from psimage.base.anno_visualizer import AnnoDescription

anno_dsc = AnnoDescription.auto_from_files(ds_path)
```

and use the created `AnnoDescription` object when calling `annotations_preview` method of PSImage.

An example of visualizing the annotations for [PATH-DT-MSU WSS1, WSS2 datasets](https://imaging.cs.msu.ru/en/research/histology/path-dt-msu) is provided in [visualize_annotations.py](./examples/visualize_annotations.py) example script.
