# Electromagnetic Waves

## What They Are

Electromagnetic waves are oscillating electric and magnetic fields propagating through space. They're created whenever an electric charge accelerates — wiggle a charged particle, and self-sustaining waves of alternating electric and magnetic fields radiate outward in all directions.

All electromagnetic waves are the same physical phenomenon. They differ only in frequency (and the inversely related wavelength). The full spectrum from low to high frequency includes radio waves, microwaves, infrared, visible light, ultraviolet, X-rays, and gamma rays.

Some reference points:

- AM broadcast radio: 535 kHz to 1.7 MHz
- FM broadcast radio: 88 to 108 MHz
- Z-Wave (US): 908 MHz
- WiFi, Bluetooth, Zigbee, microwave ovens: 2.4 GHz band
- WiFi 5 GHz / 6 GHz bands
- Visible light: ~430 to 770 THz (400-700 nm wavelength)
- X-rays and gamma rays: even higher frequencies

Visible light is an extraordinarily narrow slice of the spectrum — less than one octave out of more than 60 usable octaves.

## Made of Photons

Electromagnetic radiation is made of photons, real particles with momentum and energy but no rest mass. A photon's energy is proportional to its frequency. Higher-frequency photons (like X-rays) carry vastly more energy per photon than low-frequency ones (like radio waves).

This is why light can cause chemical changes in your retina (enough energy per photon to flip a molecule's shape) while radio waves pass through your body without measurable effect (not enough energy per photon to disrupt anything biological).

Photons aren't molecules. They have no shape, no mass, no chemistry. This is why your sense of smell and taste — which detect molecules binding to receptors — can't detect electromagnetic radiation at all. Only vision works, because it uses photon-absorption physics specifically.

## What We Can and Can't Perceive

Human senses cover an absurdly thin slice of what's physically present in any environment:

- Vision: roughly one octave of electromagnetic frequency
- Hearing: mechanical pressure waves in air, completely different physical phenomenon
- Smell and taste: chemical molecule detection, also unrelated to EM waves
- Touch: pressure, temperature, sometimes detected as infrared warmth

Things constantly present that we cannot perceive:

- Radio waves from WiFi, cellular, broadcast towers
- Cosmic microwave background radiation (afterglow of the Big Bang)
- Magnetic fields from the Earth and electrical wiring
- Neutrinos from the sun (trillions per square centimeter per second, passing through everything)
- Cosmic rays striking the upper atmosphere

Some animals get access to slightly different slices. Birds sense magnetic fields. Bees see ultraviolet. Pit vipers see infrared. Mantis shrimp have 16 types of color receptors against our 3. We've extended our perception artificially by building instruments — antennas, photodetectors, magnetometers, telescopes — that translate invisible phenomena into things we can see or read.

## How We Discovered We Could Use Them

The development of radio communication happened in distinct phases over about 70 years.

### Theoretical foundation: Maxwell, 1860s

James Clerk Maxwell unified electricity and magnetism into a single mathematical framework. His equations predicted that changing electric fields produce magnetic fields and vice versa, creating self-sustaining waves that propagate at the speed of light. Maxwell concluded that light itself was an electromagnetic wave, and that waves at other frequencies should exist and be producible by oscillating electric currents.

### Experimental verification: Hertz, 1887

Heinrich Hertz built the first deliberate radio transmitter (a spark gap) and receiver (a loop antenna with a small gap) and demonstrated that electromagnetic waves at radio frequencies existed and behaved exactly as Maxwell predicted. He thought it had no practical use.

### Engineering application: Marconi, 1890s-1900s

Guglielmo Marconi saw the practical implications Hertz had missed. He scaled up the transmitter, added antennas and grounding, and worked out how to encode Morse code by switching the spark on and off. His progression was remarkable:

- 1895: across his attic
- 1897: across the English Channel
- 1901: across the Atlantic Ocean

The transatlantic transmission worked because of the ionosphere reflecting certain frequencies — a phenomenon nobody knew about yet, partly discovered because Marconi's signal worked when it theoretically shouldn't have.

### Modulation: encoding information

Marconi only sent on/off pulses. Encoding richer information required modulation:

- AM (amplitude modulation): vary the strength of a continuous carrier wave in proportion to the audio signal. Used for voice broadcasting starting around 1906.
- FM (frequency modulation): vary the frequency of the carrier slightly. More resistant to noise. Developed in the 1930s.
- Digital modulation: encode binary data by switching between distinct combinations of frequency, phase, and amplitude. Used by every modern wireless protocol.

The conceptual leap: information doesn't have to travel as itself. Take a carrier signal that propagates well, perturb it systematically in patterns that encode your message, and reconstruct the message at the other end.

## How Wireless Communication Works Physically

A transmitter feeds an oscillating electrical current into an antenna. The antenna converts that current into an electromagnetic wave radiating outward. The wave propagates through space at the speed of light. A receiving antenna anywhere in range picks up a tiny induced current from the passing wave. The receiver amplifies and decodes this current to reconstruct the original signal.

Both ends need:

1. The same frequency (or hopping pattern)
1. The same modulation scheme
1. The same framing and protocol
1. Compatible encryption keys (for secured communications)

Speed isn't a limiting factor for terrestrial communication. New York to Los Angeles is 13 milliseconds at light speed. Around the entire planet is 130 ms. What limits range and reliability is signal strength, obstacles, interference, and noise.

## Why Frequency Choice Matters

Different frequencies have different propagation characteristics:

- Lower frequencies (longer wavelengths) diffract around obstacles, penetrate walls better, travel further
- Higher frequencies (shorter wavelengths) travel in straighter lines, get blocked more easily, but carry more data
- Frequencies below ~30 MHz can bounce off the ionosphere and travel around the world
- Frequencies above ~10 GHz are significantly absorbed by atmospheric water and oxygen

Every wireless protocol picks a frequency band based on its tradeoff between range and data rate:

- AM radio (low frequency): extreme range, terrible data rates
- FM radio: city-scale range, decent audio quality
- WiFi 2.4 GHz: room/house scale, moderate-to-high data rates
- WiFi 5 GHz and 6 GHz: smaller range, much higher data rates
- mmWave 5G: line-of-sight only, massive data rates
- Zigbee/Thread (2.4 GHz): moderate range, very low data rates, very low power
- Z-Wave (908 MHz): better range than 2.4 GHz protocols, less crowded band

The 2.4 GHz ISM band is unlicensed — anyone can transmit there without paying for spectrum rights — which is why WiFi, Bluetooth, Zigbee, Thread, baby monitors, microwave ovens, and many other things all share it. This makes it congested but accessible.

## How Many Networks Coexist in the Same Band

In a dense neighborhood, 150 WiFi networks can run in the same band because of several layered mechanisms:

### Spatial attenuation

Signal strength drops with the square of distance, and additional attenuation comes from walls and obstacles. By the time a neighbor's WiFi reaches your house, it's typically 1,000 to 100,000 times weaker than it was at their router. Your own router, being closer and unobstructed, dominates.

### Channel division

The 2.4 GHz WiFi band is split into 14 numbered channels. Routers pick a channel and broadcast on it. Networks on different non-overlapping channels (1, 6, 11 on 2.4 GHz) don't interfere at all. 5 GHz has many more available channels, which is why it works better in dense areas.

### Network identity

Every WiFi frame carries identifying information (SSID, MAC addresses). Receivers filter out anything not addressed to their network, even if the radio waves physically reach them.

### Collision avoidance

When two networks share a channel and can hear each other, they take turns via CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance). Before transmitting, a device listens for ongoing transmissions and waits if the channel is busy.

### Encryption

Modern WiFi encrypts content with WPA2 or WPA3. Even if a neighbor's receiver could decode the frames, they can't read the contents without the password.

The same principles scale up to cellular networks covering millions of users in a metro area, with additional techniques like cell-based frequency reuse, time-division scheduling, code-division multiple access, and beamforming.

## Why We Need Dedicated Hardware for Each Protocol

Your laptop's WiFi chip can't simply be reprogrammed to talk Zigbee, even though they share the 2.4 GHz band. The constraints are layered:

1. Antennas are tuned for specific frequency ranges (though somewhat flexible)
1. Analog filters and amplifiers are physically built for specific bands
1. Digital decoders are baked into silicon for specific modulation schemes
1. Real-time timing requirements demand dedicated hardware, not general-purpose CPUs
1. Power efficiency requires custom silicon — software-defined radio is 10-100x more power-hungry
1. Regulatory certification locks consumer hardware to specific protocols

Software-defined radio exists and is genuinely flexible, but it's expensive, power-hungry, and regulatorily complicated. Consumer hardware uses cheap purpose-built chips per protocol. This is why you need a Zigbee USB stick to participate in a Zigbee network even though your laptop has plenty of radios already.

## How Wireless Shaped Modern Life

The cumulative impact of taming electromagnetic waves is hard to overstate. Each layer of capability enabled new categories of human activity.

### Communication across distance

Before radio, communicating across the ocean meant physical mail by ship — weeks of delay. After Marconi, real-time ship-to-shore and intercontinental communication became routine. The Titanic disaster in 1912 was the dramatic proof: wireless distress signals from a sinking ship summoned rescue from another ship 60 miles away, saving 700 lives that would otherwise have been lost. Maritime law was rewritten the next year to require radio operators on every passenger ship.

### Broadcast media

AM and FM radio in the early 20th century created the first electronic mass media. For the first time, a single voice could reach millions of homes simultaneously. This fundamentally changed politics, advertising, music distribution, and the experience of national identity. Television added video to the same model and dominated culture for half a century.

### Aviation and navigation

Modern aviation is impossible without radio. Pilots communicate with air traffic control by voice radio, navigate using radio beacons and GPS (which is a radio system), and land in zero visibility using radio-based instrument landing systems. GPS alone — radio signals from satellites timed to nanosecond precision — has reshaped logistics, mapping, transportation, agriculture, and military operations.

### Cellular and mobile

The shift from fixed phones to mobile phones over 30 years rewired social and economic life. People are reachable anywhere. Information access is location-independent. Photo sharing, ride-hailing, real-time mapping, mobile payments, and dozens of other categories exist only because pocket-sized radios can connect to networks reliably.

### WiFi and home connectivity

WiFi's mass deployment in the early 2000s untethered computing from desks and ethernet cables. Combined with cheap laptops and later smartphones, this enabled the world where computing happens everywhere in the home, where streaming media replaces broadcast, where remote work is practical, and where every device from light bulbs to refrigerators can be networked.

### IoT and smart environments

Low-power wireless protocols like Zigbee, Thread, and Bluetooth Low Energy enable battery-powered sensors and actuators throughout buildings. Smart homes, industrial monitoring, agricultural sensing, medical wearables, and asset tracking all depend on radios small and efficient enough to run on coin cells for years.

### Scientific instrumentation

Radio astronomy reveals the structure of the universe by detecting electromagnetic waves from cosmic sources. Medical imaging (MRI, CT, X-ray) uses different parts of the spectrum to see inside the human body. Spectroscopy identifies chemical compounds by their electromagnetic signatures. Most of what we know about the universe came from learning to detect and interpret electromagnetic radiation across the spectrum.

## The Through-Line

Every device that connects wirelessly — phones, laptops, doorbells, cars, satellites, sensors — operates on physical principles first written down by Maxwell in 1865. Hertz proved them experimentally in 1887. Marconi showed they could be used for communication in the 1890s. Each subsequent decade added a layer: modulation, transistors, integrated circuits, digital signal processing, mass-produced specialized chips.

The result is that you're sitting in a room right now where invisible electromagnetic waves carrying gigabits of data per second are passing through everything, including you, constantly. Multiple WiFi networks, several cellular networks, Bluetooth devices, GPS signals from satellites, broadcast radio, and probably some smart home devices are all coexisting in the air around you, sorted out by frequency, channel, protocol, and addressing.
