# Hardware Requirements & Purchase List

## Required Hardware

### 1. Raspberry Pi
**Recommended:** Raspberry Pi Zero 2 W or Raspberry Pi 4 Model B

**Why Raspberry Pi Zero 2 W:**
- Low power consumption
- Built-in Wi-Fi
- Small form factor
- Sufficient performance for this application
- Cost-effective (~$15)

**Alternative: Raspberry Pi 4 Model B**
- More powerful (if you plan to add features)
- Better for development/testing
- More USB ports
- Higher cost (~$55)

**Purchase Links:**
- [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- [Raspberry Pi 4 Model B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)

---

### 2. MicroSD Card
**Recommended:** 16GB or 32GB Class 10 (or better)

**Specifications:**
- Minimum: 8GB (16GB recommended)
- Speed: Class 10 or UHS-I
- Format: microSDHC or microSDXC

**Purchase Options:**
- SanDisk Ultra 16GB microSDHC
- Samsung EVO Plus 32GB microSDXC
- Any reputable brand Class 10 or better

**Estimated Cost:** $5-15

---

### 3. Power Supply
**For Raspberry Pi Zero 2 W:**
- 5V, 2.5A USB power supply
- USB-A to micro-USB cable

**For Raspberry Pi 4:**
- Official Raspberry Pi USB-C power supply (5V, 3A)
- Or compatible USB-C power supply

**Purchase Options:**
- Official Raspberry Pi power supply (recommended)
- Any quality 5V USB power supply with adequate amperage

**Estimated Cost:** $8-12

---

### 4. Network Connection

**Option A: Wi-Fi (Recommended)**
- Built into Raspberry Pi Zero 2 W and Pi 4
- No additional hardware needed

**Option B: Ethernet**
- For Raspberry Pi Zero 2 W: USB to Ethernet adapter required
- For Raspberry Pi 4: Built-in Ethernet port
- Ethernet cable

**Estimated Cost:** $0 (Wi-Fi) or $5-10 (Ethernet adapter)

---

## Optional Hardware (For GPIO Approach)

### 5. PC817 Optocoupler Module
**Only needed if using GPIO trigger approach (not network-based)**

**Purpose:** Isolates 12V Denon trigger from 3.3V Raspberry Pi GPIO

**Specifications:**
- PC817 optocoupler IC
- Input: 12V compatible
- Output: 3.3V compatible
- Module format (easier to use than bare IC)

**Purchase Options:**
- PC817 Optocoupler Module (eBay, Amazon, AliExpress)
- Search: "PC817 optocoupler module"
- Typically comes with 4-8 channels

**Estimated Cost:** $2-5

**Note:** Not needed if using network-based monitoring approach (recommended).

---

### 6. Jumper Wires
**Only needed if using GPIO trigger approach**

**Purpose:** Connect optocoupler to Raspberry Pi GPIO

**Specifications:**
- Female-to-female jumper wires
- 3-4 wires needed
- 20cm length sufficient

**Purchase Options:**
- Jumper wire kit (40+ wires)
- Search: "female to female jumper wires"

**Estimated Cost:** $3-5

---

## Network-Based Approach (Recommended)

**No additional hardware needed!**

The network-based approach eliminates the need for:
- ❌ Optocoupler module
- ❌ Jumper wires
- ❌ Physical wiring between Denon and Raspberry Pi

**Requirements:**
- ✅ Raspberry Pi on same network as Denon AVR
- ✅ Denon AVR with network control enabled
- ✅ Projector with network control enabled

---

## Complete Purchase List

### Minimum Setup (Network-Based Approach)
1. Raspberry Pi Zero 2 W - **$15**
2. 16GB microSD Card - **$5**
3. USB Power Supply - **$8**
4. **Total: ~$28**

### GPIO-Based Setup (Alternative)
1. Raspberry Pi Zero 2 W - **$15**
2. 16GB microSD Card - **$5**
3. USB Power Supply - **$8**
4. PC817 Optocoupler Module - **$3**
5. Jumper Wires - **$3**
6. **Total: ~$34**

---

## Where to Buy

### Official Sources
- [Raspberry Pi Official Store](https://www.raspberrypi.com/)
- [Adafruit](https://www.adafruit.com/)
- [SparkFun](https://www.sparkfun.com/)

### General Retailers
- Amazon
- eBay
- Micro Center
- Local electronics stores

### Optocoupler & Components
- Amazon
- eBay
- AliExpress
- Digi-Key
- Mouser

---

## Additional Considerations

### Case/Enclosure (Optional)
- Protects Raspberry Pi
- Can help with heat dissipation
- Various options available ($5-15)

### Heat Sinks (Optional, for Pi 4)
- Recommended for Pi 4 under load
- Usually included with cases
- Not needed for Pi Zero 2 W

### USB Hub (Optional)
- If you need more USB ports
- Only needed for Pi Zero 2 W (has 1 USB port)

---

## Cost Summary

| Approach | Components | Estimated Cost |
|----------|-----------|----------------|
| **Network-Based** | Pi Zero 2 W + SD + Power | **~$28** |
| **GPIO-Based** | Above + Optocoupler + Wires | **~$34** |

**Recommendation:** Use network-based approach - simpler, cheaper, and more flexible.

---

## Notes

- All prices are approximate and in USD
- Prices may vary by region and retailer
- Consider buying a kit that includes multiple components
- Raspberry Pi availability can be limited - check official stock
- For production use, consider buying from official distributors

