#!/bin/bash
# Download Raspberry Pi OS Lite (64-bit) image for Pi Zero 2 W

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DOWNLOAD_DIR="$PROJECT_DIR/downloads"
IMAGE_URL="https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-07-04/2024-07-04-raspios-bookworm-arm64-lite.img.xz"
IMAGE_XZ="2024-07-04-raspios-bookworm-arm64-lite.img.xz"
IMAGE_IMG="2024-07-04-raspios-bookworm-arm64-lite.img"

echo "=========================================="
echo "Raspberry Pi OS Image Downloader"
echo "=========================================="
echo ""

# Create downloads directory
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

# Check if image already exists
if [ -f "$IMAGE_IMG" ]; then
    echo "Image already exists: $IMAGE_IMG"
    echo "Size: $(du -h "$IMAGE_IMG" | cut -f1)"
    read -p "Download again? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing image."
        exit 0
    fi
    rm -f "$IMAGE_IMG" "$IMAGE_XZ"
fi

# Check if xz file exists
if [ -f "$IMAGE_XZ" ]; then
    echo "Compressed image found: $IMAGE_XZ"
    read -p "Extract existing file? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "Extracting $IMAGE_XZ..."
        xz -d "$IMAGE_XZ"
        if [ -f "$IMAGE_IMG" ]; then
            echo "✓ Image extracted: $IMAGE_IMG"
            echo "Size: $(du -h "$IMAGE_IMG" | cut -f1)"
            exit 0
        fi
    fi
fi

# Download the image
echo "Downloading Raspberry Pi OS Lite (64-bit)..."
echo "URL: $IMAGE_URL"
echo ""
echo "This may take a while (image is ~500MB compressed, ~2GB uncompressed)..."
echo ""

# Check for curl or wget
if command -v curl &> /dev/null; then
    curl -L -o "$IMAGE_XZ" "$IMAGE_URL"
elif command -v wget &> /dev/null; then
    wget -O "$IMAGE_XZ" "$IMAGE_URL"
else
    echo "Error: Neither curl nor wget found. Please install one."
    exit 1
fi

# Extract the image
echo ""
echo "Extracting image..."
xz -d "$IMAGE_XZ"

if [ -f "$IMAGE_IMG" ]; then
    echo ""
    echo "=========================================="
    echo "✓ Download and extraction complete!"
    echo "=========================================="
    echo "Image: $DOWNLOAD_DIR/$IMAGE_IMG"
    echo "Size: $(du -h "$IMAGE_IMG" | cut -f1)"
    echo ""
    echo "Next step: Run write_image.sh to write to SD card"
    echo ""
else
    echo "Error: Extraction failed"
    exit 1
fi

