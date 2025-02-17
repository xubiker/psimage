from pathlib import Path

from PIL import Image

from psimage import PSImage

if __name__ == "__main__":
    # -- setup path to psi file
    p = Path("../data/wsi_lq.psi")
    with PSImage(p) as psim:
        # -- get width, height, magnification, tile size
        print(f"Image {psim.height} x {psim.width} at {psim.magnification}x")
        print(f"tile size {psim.layout.tile_s}")

        # -- get available previews for PSImage
        print("Previews:")
        for preview_name, preview_img in psim.previews.items():
            print(
                f"preview {preview_name}: "
                "{preview_img.width}x{preview_img.height}"
            )
            preview_img.show()

        # -- get layout
        print()
        print(psim.layout)

        # -- get all tile descriptors
        print()
        print(f"Tiles: {psim.layout.tiles_all()[:3]}...")

        # -- get all tile descriptors grouped by layer
        print()
        for layer, tiles in psim.layout.tiles_per_layer().items():
            print(f"Layer {layer}, tiles: {len(tiles)} ({tiles[:3]}...)")

        # -- get all tiles descriptors for certain layer
        print()
        tiles = psim.layout.tiles_at_layer(4)

        # -- get resolution of each layer
        print()
        for layer in psim.layout.layers:
            size = psim.layer_size(layer)
            print(f"layer {layer}, image size: {size}")

        # -- get certain tile as Image object
        tile_dsc = tiles[int(len(tiles) // 2)]
        tile_arr = psim.get_tile(tile_dsc.z, tile_dsc.pos_y, tile_dsc.pos_x)
        tile_img = Image.fromarray(tile_arr)
        tile_img.show()

        # -- you can also access tile by code
        tile_arr = psim.get_tile_by_code(tile_dsc.code)
        tile_img = Image.fromarray(tile_arr)
        tile_img.show()

        # -- you can also access tile by tile descriptor
        tile_arr = psim.get_tile_by_dsc(tile_dsc)
        tile_img = Image.fromarray(tile_arr)
        tile_img.show()

        # -- export all tiles of psimage into a folder as separate images
        # -- (n_procs param is used for multiprocessing)
        psim.export_tiles(Path("../data/out/wsi_lq_tiles"))

        # -- extract some region as Image (coordinates correspond to layer 1)
        # -- extraction chooses the best layer automatically depending on the target size
        roi = psim.get_region((10000, 10000), (15000, 16000), (500, 600))
        Image.fromarray(roi).show()

        # -- or you can extract some region from certain layer
        # -- in this case coordinates correspond to the desired layer
        roi = psim.get_region_from_layer(64, (100, 150), (250, 250))
        Image.fromarray(roi).show()

        # -- you can export a downscaled version of PSImage as Image to file
        # -- you can specify scale or desired resolution
        psim.export_simple(Path("../data/out/export_1.jpg"), scale=0.1)
        psim.export_simple(Path("../data/out/export_2.jpg"), max_side=2000)

    # # -- if you don't want to use 'with' statement you can close PSImage manually
    psimage = PSImage(p)
    print(psimage.codec, psimage.quality)
    psimage.close()
