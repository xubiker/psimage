from pathlib import Path

from psimage import PSImage

if __name__ == "__main__":
    # -- setup path to psi file
    p = Path("./data/images/test_01.psi")
    with PSImage(p) as psim:
        # -- get width, height, magnification, tile size
        print(f"Image {psim.height} x {psim.width} at {psim.magnification}x")
        print(f"tile size {psim.layout.tile_s}")

        # -- get available previews for PSImage
        print("Previews:")
        for preview_name, preview_img in psim.previews.items():
            print(f"preview {preview_name}: {preview_img.width}x{preview_img.height}")
            # preview_img.show()

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
        tile_img = psim.get_tile(tile_dsc.z, tile_dsc.target_y, tile_dsc.target_x)
        # tile_img.show()

        # -- you can also access tile by code
        tile_img = psim.get_tile_by_code(tile_dsc.code)
        # tile_img.show()

        # -- export all tiles of psimage into a folder as separate images
        # -- (n_procs param is used for multiprocessing)
        # psim.export_tiles(
        #   Path("./data/images/test_01.psi")
        # )

        # -- extract some region as Image (coordinates correspond to layer 1)
        # -- extraction chooses the best layer automatically depending on the target size
        roi = psim.get_region((1000, 1000), (2000, 3000), (500, 1000))
        # roi.show()

        # -- or you can extract some region from certain layer
        # -- in this case coordinates correspond to the desired layer
        roi = psim.get_region_from_layer(2, (100, 150), (250, 250))
        # roi.show()

        # -- you can export a downscaled version of PSImage as Image to file
        # -- you can specify scale or desired resolution
        # psim.export_simple(Path(".") / "export_1.jpg", scale=0.1)
        # psim.export_simple(Path(".") / "export_2.jpg", max_size=2000)

    # -- if you don't want to use 'with' statement you can close PSImage manually
    psimage = PSImage(p)
    print(psimage.codec, psimage.quality)
    psimage.close()
