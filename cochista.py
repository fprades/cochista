import argparse
from codecs import raw_unicode_escape_encode
import json
import random
import re
from string import Template
import sys
import urllib.request
from pathlib import Path
from shutil import copyfile, copyfileobj
from time import sleep
from urllib.parse import urlencode, urljoin

import lxml.etree as etree
import pandas

regex = re.compile("JSON.parse\((.*)\)")

XPATH = """//script[contains(text(), "__INITIAL_PROPS__")]"""


def _user_agent():
    os = random.choice(
        [
            "Macintosh; Intel Mac OS X 10.15; rv:95.0",
            "Windows NT 10.0; Win64; x64; rv:103.0",
        ]
    )
    i = random.randint(90, 106)
    return f"Mozilla/5.0 ({os}) Gecko/20100101 Firefox/{i}.0"


def _accept_language():
    es = ["es-AR", "es-CL", "es-PE", "es-ES"]
    random.shuffle(es)
    q = random.uniform(0.2, 0.9)
    return f"""{", ".join(es)}, es, en-US, en; q={q:.1}"""


def _headers():
    return {
        "User-Agent": _user_agent(),
        "Accept-Encoding": "deflate, br",
        "Accept-Language": _accept_language(),
    }


def feed(
    name: str,
    pages: int = 10,
    pause: float = 10,
    base="https://www.coches.net",
    datadir: Path = Path("data"),
    **kwargs,
):

    query = urljoin(base, f"{name}/")
    query = urljoin(query, "segunda-mano/")

    where = datadir / name
    where.mkdir(exist_ok=True, parents=True)

    for page in range(pages):
        file = where / f"data.{page+1}.html"
        if not file.exists():
            request = urllib.request.Request(
                query + "?" + urlencode(dict(**kwargs, pg=page + 1)),
                headers=_headers(),
            )
            print(request.full_url, file, request.headers)
            with urllib.request.urlopen(request) as response, open(file, "wb") as dst:
                copyfileobj(response, dst)

            doc = etree.parse(file, etree.HTMLParser())
            if not doc.xpath(XPATH):
                print("Error:", file)
                file.rename(file.with_name(f"_error{page+1}.html"))

            sleep(pause)


def coches(name: str, datadir: Path = Path("data")):

    coches = []

    for file in (datadir / name).glob("data.*.html"):
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


def createweb(name: str, datadir: Path = Path("data"), outdir: Path = Path("docs")):
    webdir = outdir / name
    webdir.mkdir(exist_ok=True, parents=True)
    coches(name, datadir=datadir).to_json(
        f"""{webdir/"data.json"}""", indent=2, orient="records"
    )
    template = Template(Path("template.html").read_text())
    (webdir / "index.html").write_text(template.substitute(name = name))


def main(argv):
    """
    "Cochista" extracts data from coches.net and creates a D3 graph with the ads for analysis
    """

    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument("--datadir", type=Path, default=Path("data"))
    parser.add_argument("--outdir", type=Path, default=Path("docs"))
    parser.add_argument("--pages", type=int, default=10)
    parser.add_argument("--pause", type=float, default=2)
    parser.add_argument("queries", nargs="*")

    opts = parser.parse_args(argv)

    for query in opts.queries:
        print(query)
        feed(name=query, pages=opts.pages, pause=opts.pause, datadir=opts.datadir)
        createweb(name=query, outdir=opts.outdir)


if __name__ == "__main__":
    main(sys.argv[1:])
