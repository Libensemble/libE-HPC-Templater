from setuptools import setup


if __name__ == "__main__":
    setup(
        name="libe-templater",
        install_requires=["Jinja2", "psij-python", "Click"],
        python_requires=">=3.8",
        entry_points={"console_scripts": ["templater = cli:main"]},
    )
