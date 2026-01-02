#!/bin/bash
# Write Raspberry Pi OS image to SD card

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DOWNLOAD_DIR="$PROJECT_DIR/downloads"
IMAGE_IMG="2024-07-04-raspios-bookworm-arm64-lite.img"

echo "=========================================="
echo "Raspberry Pi OS Image Writer"
echo "=========================================="
echo ""

# Check if image exists
if [ ! -f "$DOWNLOAD_DIR/$IMAGE_IMG" ]; then
    echo "Error: Image not found: $DOWNLOAD_DIR/$IMAGE_IMG"
    echo "Run download_image.sh first"
    exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS"
    
    # List disks
    echo ""
    echo "Available disks:"
    diskutil list
    
    echo ""
    echo "IMPORTANT: Identify your SD card from the list above."
    echo "Look for the disk that matches your SD card size."
    echo ""
    read -p "Enter the disk identifier (e.g., disk2, NOT disk2s1): " DISK
    
    if [ -z "$DISK" ]; then
        echo "Error: No disk specified"
        exit 1
    fi
    
    # Safety check
    echo ""
    echo "WARNING: This will ERASE all data on /dev/$DISK"
    echo "Target: /dev/$DISK"
    echo "Image: $DOWNLOAD_DIR/$IMAGE_IMG"
    echo ""
    read -p "Are you absolutely sure? Type 'yes' to continue: " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
    
    # Unmount the disk
    echo ""
    echo "Unmounting disk..."
    diskutil unmountDisk /dev/$DISK || true
    
    # Write the image
    echo ""
    echo "Writing image to SD card..."
    echo "This may take 5-15 minutes depending on SD card speed..."
    echo ""
    
    sudo dd if="$DOWNLOAD_DIR/$IMAGE_IMG" of=/dev/r$DISK bs=1m status=progress
    
    # Sync
    echo ""
    echo "Syncing..."
    sync
    
    # Wait a moment for disk to be ready
    sleep 2
    
    # Configure SSH and user account
    echo ""
    echo "Configuring SSH and user account..."
    
    # Find the boot partition (usually the first partition)
    BOOT_PARTITION="/dev/${DISK}s1"
    
    # Mount the boot partition
    MOUNT_POINT=$(mktemp -d)
    sudo mount -t msdos "$BOOT_PARTITION" "$MOUNT_POINT" 2>/dev/null || sudo mount -t vfat "$BOOT_PARTITION" "$MOUNT_POINT"
    
    # Enable SSH
    echo "Enabling SSH..."
    sudo touch "$MOUNT_POINT/ssh"
    
    # Create admin user with password "admin"
    echo "Creating admin user..."
    # Generate password hash for "admin" using openssl
    PASSWORD_HASH=$(openssl passwd -6 admin 2>/dev/null || python3 -c "import crypt; print(crypt.crypt('admin', crypt.mksalt(crypt.METHOD_SHA512)))")
    
    # Create userconf file (format: username:password_hash)
    echo "admin:$PASSWORD_HASH" | sudo tee "$MOUNT_POINT/userconf" > /dev/null
    
    # Unmount
    sudo umount "$MOUNT_POINT"
    rmdir "$MOUNT_POINT"
    
    echo ""
    echo "=========================================="
    echo "✓ Image written and configured successfully!"
    echo "=========================================="
    echo ""
    echo "Configuration:"
    echo "  - SSH: Enabled"
    echo "  - Username: admin"
    echo "  - Password: admin"
    echo ""
    echo "Next steps:"
    echo "1. Eject the SD card safely"
    echo "2. Insert it into your Raspberry Pi Zero 2 W"
    echo "3. Power on the Pi"
    echo "4. Find the Pi's IP address and SSH in:"
    echo "   ssh admin@<pi_ip>"
    echo ""
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Detected Linux"
    
    # List disks
    echo ""
    echo "Available disks:"
    lsblk
    
    echo ""
    echo "IMPORTANT: Identify your SD card from the list above."
    echo "Look for the disk that matches your SD card size."
    echo ""
    read -p "Enter the disk path (e.g., /dev/sdb, NOT /dev/sdb1): " DISK
    
    if [ -z "$DISK" ]; then
        echo "Error: No disk specified"
        exit 1
    fi
    
    # Safety check
    echo ""
    echo "WARNING: This will ERASE all data on $DISK"
    echo "Target: $DISK"
    echo "Image: $DOWNLOAD_DIR/$IMAGE_IMG"
    echo ""
    read -p "Are you absolutely sure? Type 'yes' to continue: " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
    
    # Unmount partitions
    echo ""
    echo "Unmounting partitions..."
    sudo umount ${DISK}* 2>/dev/null || true
    
    # Write the image
    echo ""
    echo "Writing image to SD card..."
    echo "This may take 5-15 minutes depending on SD card speed..."
    echo ""
    
    sudo dd if="$DOWNLOAD_DIR/$IMAGE_IMG" of="$DISK" bs=4M status=progress oflag=sync
    
    # Sync
    echo ""
    echo "Syncing..."
    sync
    
    # Wait a moment for disk to be ready
    sleep 2
    
    # Configure SSH and user account
    echo ""
    echo "Configuring SSH and user account..."
    
    # Find the boot partition (usually the first partition)
    BOOT_PARTITION="${DISK}1"
    
    # Mount the boot partition
    MOUNT_POINT=$(mktemp -d)
    sudo mount "$BOOT_PARTITION" "$MOUNT_POINT"
    
    # Enable SSH
    echo "Enabling SSH..."
    sudo touch "$MOUNT_POINT/ssh"
    
    # Create admin user with password "admin"
    echo "Creating admin user..."
    # Generate password hash for "admin"
    PASSWORD_HASH=$(openssl passwd -6 admin 2>/dev/null || python3 -c "import crypt; print(crypt.crypt('admin', crypt.mksalt(crypt.METHOD_SHA512)))")
    
    # Create userconf file (format: username:password_hash)
    echo "admin:$PASSWORD_HASH" | sudo tee "$MOUNT_POINT/userconf" > /dev/null
    
    # Unmount
    sudo umount "$MOUNT_POINT"
    rmdir "$MOUNT_POINT"
    
    echo ""
    echo "=========================================="
    echo "✓ Image written and configured successfully!"
    echo "=========================================="
    echo ""
    echo "Configuration:"
    echo "  - SSH: Enabled"
    echo "  - Username: admin"
    echo "  - Password: admin"
    echo ""
    echo "Next steps:"
    echo "1. Eject the SD card safely"
    echo "2. Insert it into your Raspberry Pi Zero 2 W"
    echo "3. Power on the Pi"
    echo "4. Find the Pi's IP address and SSH in:"
    echo "   ssh admin@<pi_ip>"
    echo ""
    
else
    echo "Error: Unsupported OS: $OSTYPE"
    echo "This script supports macOS and Linux"
    exit 1
fi

