from setuptools import setup

setup(
    name="vault-toolbox",
    version="0.1",
    py_modules=["vault_toolbox"],
    entry_points="""
        [console_scripts]
        vault-toolbox=vault_toolbox:main
    """,
)
