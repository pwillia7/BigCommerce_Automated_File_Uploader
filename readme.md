# BigCommerce Automated File Uploader

## Description

The BigCommerce Automated File Uploader is a Python script that automates the process of uploading files to products in a BigCommerce store. This script uses Selenium to interact with the BigCommerce admin interface, simulating user actions to upload files since file upload is not available via API or CSV. 

[Video demo can be found here.](https://www.youtube.com/watch?v=7TEtB1QpJlE)

## Requirements

- Python 3.x
- Selenium
- Google Chrome
- ChromeDriver

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/BigCommerce-Automated-File-Uploader.git
   cd BigCommerce-Automated-File-Uploader
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install selenium
   ```

4. **Download and install ChromeDriver:**
   - Ensure you have the correct version of ChromeDriver that matches your installed version of Google Chrome.
   - At this link, under 'Stable', download the binary for chromedriver (NOT chrome) for your platform: https://getwebdriver.com/chromedriver
   - Place the ChromeDriver executable in a directory included in your system's PATH, or specify the path in the `config.json` file.

## Configuration

1. **Replace the values in the `config.json` file in the root directory of the project:**
   ```json
   {
     "username": "your-email@example.com",
     "password": "your-password",
     "store_hash": "store-hash",
     "start_product_id": 100,
     "end_product_id": 200,
     "driver_path": "/path/to/chromedriver"
   }
   ```
## File Organization

To use the BigCommerce Automated File Uploader, you need to organize your product files in a specific folder structure. Each subfolder should be named according to the product identifier type you are using (`id`, `sku`, or `name`). Inside each subfolder, place the files you want to upload for that product.

Here is an example folder tree structure:

```
/path/to/your/files
├── 1001
│   ├── file1.png
│   └── file2.jpg
├── 1002
│   ├── file1.png
│   └── file2.jpg
└── 1003
    ├── file1.png
    └── file2.jpg
```

In this example, each subfolder (`1001`, `1002`, `1003`) represents a product identifier. The files inside each subfolder (`file1.png`, `file2.jpg`) are the files to be uploaded for that product.


## Usage

1. **Run the script:**
   ```bash
   python main.py ./product_files name
   ```

   - `./product_files`: The path to the folder containing the product subfolders.
   - `name`: The type of identifier used for subfolder names (`id`, `sku`, or `name`).

## Notes

- The script will prompt you to complete the 2FA process during execution.
- The script will upload files to products within the specified product ID range.
- Ensure your file paths and subfolder names are correctly set up to match the product identifiers.

## Troubleshooting

- If you encounter issues with the ChromeDriver version, ensure it matches your installed version of Google Chrome.
- Verify the paths in your `config.json` file are correct.
- Check for any errors in the console output and ensure all dependencies are installed correctly.

## TODO
* handle variable productID range
* add support for other file upload fields
* wildcard support on names/sku
* support file overwrite/deletion
* Other input support -- CSV? DB?