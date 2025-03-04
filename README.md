# Bach-o-mat: Electromechanical MIDI Player for Keyboards

| ![](hardware/assembly_media/device_on_piano_2.png) | ![](hardware/assembly_media/complete_device_2.png) |
| --------------------- | --------------------------- |

Bach-o-mat is an open-source electromechanical device designed to play **pipe organs**, but it can also be used on any **keyboard instrument**. It operates using **Arduino and micro servomotors**, allowing it to play music by interfacing with a **MIDI control device**.

## How It Works
A control device (such as a **PC or smartphone**) connects to Bach-o-mat via **USB** (with **Bluetooth support coming soon**) and sends MIDI signals to activate the keyboard's notes.

The system is designed for **58-note keyboards**, a standard commonly used in **pipe organs until the late 19th century**. However, thanks to its **modular design**, it consists of separate **modules** for:
- Each **octave of natural keys**
- Each **octave of accidental keys**

This allows users to **easily build versions for larger keyboards**. The modular structure also enables **horizontal adjustments**, making it adaptable to keyboards with **different key widths**. Additionally, the **side supports** can slide freely, allowing flexible placement on different instruments.

## Repository Structure
This repository contains everything needed to build and operate Bach-o-mat:

```
Bach-o-mat/
│── firmware/        # Code for Arduino and microcontrollers
│── hardware/        # 3D printable models and 2D design files
│── docs/            # Assembly instructions and schematics
│── README.md        # Project introduction
│── LICENSE          # Open-source license
```

### `hardware/`
- **3D models** for 3D printing
- **2D design files** for laser cutting and CNC machining
- **Wiring schematics** and component diagrams

### `firmware/`
- **Arduino source code** for controlling the servomotors
- **Configuration files** for MIDI input handling

## Getting Started
To build Bach-o-mat, follow these steps:
1. **Download** the design files from [`hardware/`](hardware/)
2. **Print** the necessary 3D components or cut the 2D parts
3. **Assemble** the modules following the guide in [`docs/`](docs/)
4. **Upload** the firmware from [`firmware/`](firmware/) to an Arduino board
5. **Connect** the device via USB to a MIDI control source
6. **Play music**

## Demonstration
A video demonstration of Bach-o-mat in action is available:

[![Setup on Organ Playing](images/youtube-thumbnail.png)](https://youtu.be/sfZ5kHSBi4M?si=fCr5qvPlyGegtceW)

## Future Improvements
- **Bluetooth connectivity** for wireless control
- **Expanded keyboard support** for even larger instruments
- **Optimized motor response** for improved playability

## License
Bach-o-mat is released under the **GNU General Public License**, making it freely available for modification and use. If you improve the project, consider contributing your modifications back to the community.

---

For any inquiries or contributions, please open an **Issue** or submit a **Pull Request**.

