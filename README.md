# psimage
PSImage is a python package to work with images in ```psi``` format, that are used in *pathscribe* software.

## Installation

```
pip install psimage-0.0.1-py3-none-any.whl
```

## Sample data
Sample images in ```psi``` format can be found here:
- https://disk.yandex.ru/d/mu5ciY3dBG51jQ (PATH-DT-MSU WSS1 dataset),
- https://disk.yandex.ru/d/x2rstRs26qx_mQ (PATH-DT-MSU WSS2 dataset).

## Usage

#### Open image
You can work with locally stored images in ```psi``` format and either use with clause:
```python
from pathlib import Path
from psimage import PSImage
p = Path("./data/images/test_01.psi")
with PSImage(p) as psim:
    ...
```
or you can manually open and close image:
```python
from pathlib import Path
from psimage import PSImage
p = Path("./data/images/test_01.psi")
psim = PSImage(p)
...
psim.close()
```

#### Get general image properties and previews
```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/images/test_01.psi")
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

#### Work with layout and individual tiles
In ```psi``` format the image is stored as a pyramid of tiles. The layers of the pyramid are numbered by powers of two (1, 2, 4, 8, 16, ...). The resolution of each superior layer is 2 times smaller. Each layer consists of tiles. The top layer of the pyramid consists of only one tile. Almost all tiles (except last row and last column) are small images of ```tile_size``` size.
To work with pyramid structure there is a ```TilesLayout``` class.

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/images/test_01.psi")
with PSImage(p) as psim:
    # -- get resolution of each layer
    print()
    for layer in psim.layout.layers:
        size = psim.layer_size(layer)
        print(f"layer {layer}, image size: {size}")
```

```
layer 1, image size: (26880, 31744)
layer 2, image size: (13440, 15872)
layer 4, image size: (6720, 7936)
layer 8, image size: (3360, 3968)
layer 16, image size: (1680, 1984)
layer 32, image size: (840, 992)
layer 64, image size: (420, 496)
```

Each tile in the pyramid is specified by ```TileDescriptor``` class. It contains the coordinates of the tile: ```z``` corresponds to layer index, ```y, x``` correspond to the position of the tile inside layer.

You can get all tile descriptors for the image or get them grouped by layers or get tile descriptors for the specific layer.

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/images/test_01.psi")
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

To get the tile image as *Pillow Image* object using tile descriptor you can either call method ```get_tile``` and pass ```z, y, x``` coordinates of the tile to it or call ```get_tile_by_code``` method and pass descriptor's code to it.

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/images/test_01.psi")
with PSImage(p) as psim:
    tiles = psim.layout.tiles_at_layer(4)
    tile_dsc = tiles[int(len(tiles) // 2)]

    # -- access tile by coordinates
    tile_img = psim.get_tile(tile_dsc.z, tile_dsc.target_y, tile_dsc.target_x)
    tile_img.show()

    # -- access tile by code
    tile_img = psim.get_tile_by_code(tile_dsc.code)
```


#### Extract arbitary regions from ```psi``` image
There are 2 ways to access arbitary regions of the image.

Firstly you can call ```get_region``` and pass the TL and BR coordinates (in terms of layer 1 resolution) of the desired rectangle and the target resolution of the desired region. In this way the best layer for extraction is choosen automatically depending on the specified sizes.

Secondly you can call ```get_region_from_layer``` and pass the index of the layer (1, 2, 4, 8, ...) and the TL and BR coordinates of the rectangle region.

Both methods return *Pillow Image* object.

```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/images/test_01.psi")
with PSImage(p) as psim:
as Image (coordinates correspond to layer 1)
    # -- extract region (choose the best layer automatically)
    roi = psim.get_region((1000, 1000), (2000, 3000), (500, 1000))
    roi.show()

    # -- extract some region from certain layer
    roi = psim.get_region_from_layer(2, (100, 150), (250, 250))
    roi.show()
```

#### Export from ```psi``` format
You can export all tiles of an image to a given folder using ```export_tiles``` method.
Or you can export a downscaled version of the image using ```export_simple``` method. In this case you either pass the downscale factor or the maximum size of the image (considered on the larger side).
```python
from pathlib import Path
from psimage import PSImage

p = Path("./data/images/test_01.psi")
with PSImage(p) as psim:
    # -- export all tiles of psimage into a folder as separate images
    # -- (n_procs param is used for multiprocessing)
    psim.export_tiles(Path(".data/test_01_tiles/"))

    # -- specify scale or desired resolution
    psim.export_simple(Path(".") / "export_1.jpg", scale=0.1)
    psim.export_simple(Path(".") / "export_2.jpg", max_size=2000)

```