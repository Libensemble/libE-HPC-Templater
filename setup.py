from setuptools import setup


if __name__ == '__main__':
    setup(
        name='libe-templater',
        scripts=["templater"],
        install_requires=["Jinja2", "psij-python"],
        python_requires='>=3.8'
    )
