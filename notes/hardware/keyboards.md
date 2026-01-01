# How Keyboards Work & Wooting Technology

## Traditional Keyboard Mechanics

Keyboards use a matrix circuit to track all keys from a single circuit rather than requiring hundreds of individual connections. Keys are arranged in a grid of rows and columns - the controller scans through by sending signals down each column and checking which rows complete the circuit. When you press a key, it closes a switch at a specific row-column intersection, and the controller identifies that unique coordinate.

### From Key Press to Character

1. The controller maintains a lookup table (firmware) that maps each row-column position to a scan code - a numeric identifier for that physical key position
1. The scan code is sent to your computer via USB HID (Human Interface Device) protocol
1. Your OS interprets the scan code based on your configured keyboard layout and delivers the character to the active application

### Traditional Actuation

On standard mechanical keyboards, a key registers when the switch mechanism makes contact - typically around 2mm into a ~4mm total travel. The actuation point is fixed by physical switch design and cannot be changed.

______________________________________________________________________

## Wooting's Hall Effect Technology

### How It Works

Instead of binary contact switches, Wooting keyboards use Hall effect sensors - magnets positioned at the base of each switch with sensors on the PCB that detect exactly how far the key has traveled. This provides continuous position data with 0.1mm precision throughout the entire keystroke.

### What This Enables

Adjustable Actuation Points

- Define in software exactly where (0.1mm–4.0mm) a key should register
- Different keys can have different actuation points
- Example: Set WASD to 0.1mm for instant response, spacebar to 0.5mm to avoid accidental presses

Rapid Trigger

- Instead of waiting for a key to return past a fixed reset point, the keyboard detects direction changes
- The moment you reverse direction by the sensitivity threshold (e.g., 0.40mm), the key state flips
- Eliminates wasted travel time when releasing and re-pressing keys
- Particularly valuable for fast strafing in FPS games - direction changes happen faster because you're not fighting a fixed reset point

### Actuation Point vs Rapid Trigger

These are independent features, both enabled by continuous position sensing:

| Feature | What It Controls |
| --------------- | --------------------------------------------------------------------------------------------------- |
| Actuation Point | How far down must I press before the key registers? (The "entry gate") |
| Rapid Trigger | After pressing, how is release/re-press determined? (Based on direction change, not fixed position) |

Traditional keyboards can't do either because they only know two states: contact made or contact broken. They have no idea where the key is between those points.

______________________________________________________________________

## Polling Rate

Definition: How many times per second the keyboard reports its state to the OS.

| Rate | Interval |
| ------- | ------------- |
| 1000 Hz | Every 1ms |
| 8000 Hz | Every 0.125ms |

Potential downsides of high polling rates:

- Slightly increased CPU usage (negligible on modern systems)
- USB bandwidth concerns with multiple high-polling devices
- Rare compatibility issues with certain motherboards/USB controllers

For most setups, maximum polling rate is ideal.

______________________________________________________________________

## Other Wooting Features

Debounce Filter: Traditional mechanical keyboards require debounce filtering because metal contacts bounce when they connect, causing false double-presses. Hall effect switches are contactless, so no debounce is needed - keeping it off means zero debounce delay.

Continuous Rapid Trigger: When enabled, allows spamming a key without ever needing to hit the actuation point again after the first press.

______________________________________________________________________

## Key Takeaway

Hall effect sensing transforms a keyboard from a binary input device ("pressed or not") into an analog input device streaming continuous position data. This enables both adjustable actuation points and rapid trigger - the OS knows about state changes instantly based on movement direction rather than waiting for keys to cross fixed thresholds.
