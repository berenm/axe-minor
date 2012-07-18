from distutils.core import setup
from Pyrex.Distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(
  name = 'lzss',
  ext_modules=[ Extension("lzss", ["lzss.pyx"]) ],
  cmdclass = {'build': build_ext}
)
