from setuptools import setup, find_packages

setup(
    name="shogiimagesolver",
    version="0.3",
    packages=find_packages(),
    include_package_data=False,
    install_requires=["numpy", "opencv-contrib-python", "Pillow", "python-shogi"],
)
