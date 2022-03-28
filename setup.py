import os
from codecs import open
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

package = "rpcm"

about = {}
with open(os.path.join(here, package, "__about__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

def readme():
    with open(os.path.join(here, 'README.md'), 'r', 'utf-8') as f:
        return f.read()

requirements = ['numpy',
                'pyproj',
                'geojson',
                'rasterio[s3]>=1.2',
                'srtm4>=1.0.2']

extras_require = {'test': ['pytest']}

setup(name=about["__title__"],
      version=about["__version__"],
      description=about["__description__"],
      long_description=readme(),
      long_description_content_type='text/markdown',
      url=about["__url__"],
      author=about["__author__"],
      author_email=about["__author_email__"],
      packages=[package],
      install_requires=requirements,
      extras_require=extras_require,
      python_requires=">=3",
      entry_points="""
          [console_scripts]
          rpcm=rpcm.cli:main
      """)
