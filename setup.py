from setuptools import setup, find_packages

setup(
    name='abm_framework',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    author='Raphael M. S. de Jesus',
    description='Framework genérica para simulações baseadas em agentes (ABM)',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.8',
)
