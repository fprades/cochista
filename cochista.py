from shutil import copyfile, copyfileobj
from time import sleep
from urllib.parse import urlencode, urljoin
import lxml.etree as etree
import json
import re
import pathlib
import urllib.request

import random

import pandas

regex = re.compile("JSON.parse\((.*)\)")

XPATH = """//script[contains(text(), "__INITIAL_PROPS__")]"""

USER_AGENTS = [
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/{i}.0" for i in range(90,106)
]
    
    #"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",



def feed(name: str, pages: int = 10, pause:float=10, base="https://www.coches.net", **kwargs):

    query = urljoin(base, f"{name}/")
    query = urljoin(query, "segunda-mano/")

    where = pathlib.Path(name)
    where.mkdir(exist_ok=True, parents=True)

    for page in range(pages):
        file = where / f"data.{page+1}.html"
        if not file.exists():
            request = urllib.request.Request(
                query + "?" +urlencode(dict(**kwargs, pg=page+1)),
                headers={
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept-Encoding": "deflate, br",
                    "Accept-Language": f"es-CL, es-ES, es, en-US, en; q={round(random.uniform(0.2, 0.9),1)}"
                },
            )
            print(request.full_url, file, request.headers)
            with urllib.request.urlopen(request) as response, open(file, "wb") as dst:
                copyfileobj(response, dst)

            doc = etree.parse(file, etree.HTMLParser())
            if not doc.xpath(XPATH):
                print("Error:", file)
                file.rename(file.with_name(f"_error{page+1}.html"))
           
            sleep(pause)


def coches(name: str):

    coches = []

    for file in pathlib.Path(name).glob("data.*.html"):
        doc = etree.parse(file, etree.HTMLParser())

        script = doc.xpath(XPATH)

        if not script:
            print("Skipping:", file)
            continue

        result = regex.search(script[0].text)
        result = result.group(1)
        result = eval(result)

        result = json.loads(result)

        for r in result["initialResults"]["items"]:
            for k in "photos", "imgUrl":
                r.pop(k, None)
            coches.append(r)

    return pandas.DataFrame(coches)

def createweb(name: str):
    coches(name).to_json(f"{name}/data.json", indent=2, orient="records")
    copyfile("template.html", f"{name}/index.html")

