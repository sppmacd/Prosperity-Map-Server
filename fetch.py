import json
import math
import traceback

import caching
import datetime
from PIL import Image, ImageDraw
import io
import os
import sys
import tqdm

URL = "map.prosperitymc.net"


def build_url(dimension: str, zoom: int, region_coords: tuple[int, int]):
    return f"https://{URL}/tiles/minecraft_{dimension}/{zoom}/{region_coords[0]}_{region_coords[1]}.png"


def download_image(dimension: str, zoom: int, region_coords: tuple[int, int]):
    u = build_url(dimension, zoom, region_coords)
    # print(u)
    return caching.get(u)


# x,z min max are in blocks
def build_full_map(name: str, dimension: str, xminmax: tuple[int, int], zminmax: tuple[int, int], *, zoom: int = 3,
                   scaledown: int = 1):
    date_string = datetime.datetime.now().strftime('%Y-%m-%d')
    cache_dir = f"cache_{date_string}"

    print(
        f"{name}: {dimension} X={xminmax[0]}..{xminmax[1]} Z={zminmax[0]}..{zminmax[1]} zoom={zoom} scaledown={scaledown}")

    if os.path.exists(cache_dir):
        os.rename(cache_dir, "cache")

    os.makedirs(f"maps/{date_string}", exist_ok=True)

    REGION_SIZES = [4096, 2048, 1024, 512]
    PX_PER_REGION = 512 // scaledown
    xmin = xminmax[0]
    xmax = xminmax[1]
    zmin = zminmax[0]
    zmax = zminmax[1]

    def save_image():
        img.save(
            f"maps/{date_string}/{name}.png")

    try:
        xrange = range(math.floor(xmin / REGION_SIZES[zoom]), math.ceil(xmax / REGION_SIZES[zoom]))
        zrange = range(math.floor(zmin / REGION_SIZES[zoom]), math.ceil(zmax / REGION_SIZES[zoom]))

        count = len(xrange) * len(zrange)
        # print(xrange, zrange)

        imgsize = (len(xrange) * PX_PER_REGION, len(zrange) * PX_PER_REGION)
        # print(imgsize)
        img = Image.new(mode='RGB', size=imgsize)

        with tqdm.tqdm(total=count) as pbar:
            for x in xrange:
                for z in zrange:
                    idx = len(zrange) * (x - xrange.start) + z - zrange.start
                    # print(f"loading {dimension},{x},{z} {idx}/{count} {idx * 100 / (count):.2f}%")
                    region = download_image(dimension, zoom, (x, z))
                    if len(region) == 0:
                        imgdraw = ImageDraw.Draw(img)
                        imgdraw.rectangle(((PX_PER_REGION * (x - xrange.start), PX_PER_REGION * (z - zrange.start)),
                                           (
                                               PX_PER_REGION * (x - xrange.start + 1),
                                               PX_PER_REGION * (z - zrange.start + 1))),
                                          fill="#303040")
                    else:
                        region_img = Image.open(io.BytesIO(region))
                        img.paste(region_img.resize((PX_PER_REGION, PX_PER_REGION)),
                                  (PX_PER_REGION * (x - xrange.start), PX_PER_REGION * (z - zrange.start)))

                    if idx % 1000 == 0:
                        save_image()

                    pbar.update()
    except KeyboardInterrupt:
        pass
    finally:
        os.rename("cache", cache_dir)
        save_image()


with open("areas.json") as f:
    areas = json.load(f)

for name, area in areas.items():
    dimension = area["dimension"]
    xrange = (area["xmin"], area["xmax"])
    zrange = (area["zmin"], area["zmax"])
    zoom = area["zoom"]
    scaledown = area.get("scaledown") or 1

    try:
        build_full_map(name, dimension, xrange, zrange, zoom=zoom, scaledown=scaledown)
    except Exception:
        print(traceback.format_exc())
