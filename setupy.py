from setuptools import setup

setup(name='PKPy',
      version='0.1',
      description='A package to solve simple pharmacokinetic models.',
      author=[ "James Broster", "Ronald Cvek", "Hamlet Khachatryan", "Odysseas Vavourakis"]
      packages=['PKPy'],
      install_requires = ["numpy", "matplotlib", "scipy"],
      license='MIT')