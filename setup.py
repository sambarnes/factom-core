from setuptools import (
    setup,
    find_packages,
)


deps = {
    'factom-core': [
        'factom-keys',
        'plyvel',
    ],
    'hydra': [
        'bottle',
        'click',
        'plyvel',
        'requests',
    ]
}

setup(
    name='factom-core',
    version='0.0.3',
    description='A python library for working with the primitives of the Factom blockchain',
    author="Sam Barnes",
    author_email="mistersamuelbarnes@gmail.com",
    url='https://github.com/sambarnes/factom-core',
    keywords=['factom', 'core', 'blockchain'],
    license='MIT',
    py_modules=['factom_core'],
    install_requires=deps['factom-core'],
    zip_safe=False,
    packages=find_packages(exclude=["tests", "tests.*", "hydra", "p2p"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
