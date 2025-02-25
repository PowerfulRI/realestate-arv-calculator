from setuptools import setup, find_packages

setup(
    name="realestate_arv_app",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'anthropic',
        'selenium',
        'webdriver-manager',
        'beautifulsoup4',
        'python-dateutil',
        'requests',
        'pandas',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'arv-calculator=realestate_arv_app.main:main',
        ],
    },
    author="Real Estate ARV Team",
    author_email="info@example.com",
    description="Real Estate ARV (After Repair Value) Calculator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/realestate-arv-calculator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)