# Sound

## Sound and waves

Sound is pressure waves traveling through a medium (usually air). Vocal cords, guitar strings, or speakers push air molecules, creating alternating compression and rarefaction that propagates outward.

A wave has a few key properties:

- Frequency — how many cycles per second (Hz). Determines pitch for sound, "color" for radio.
- Amplitude — the height of the wave. Determines loudness for sound, signal strength for radio.
- Waveform — the *shape* of the wave over time. Determines timbre (why a guitar and piano playing the same note sound different).

Human voice ranges roughly 300 Hz – 3 kHz for intelligibility. Hearing tops out around 20 kHz.

## Transducers — converting between domains

A transducer converts one form of energy into another. Almost every signal chain starts and ends with one.

- Microphone: pressure waves -> electrical signal
  - *Carbon* (WWII): sound vibrates a diaphragm pressing on carbon granules, changing resistance
  - *Dynamic*: diaphragm moves a coil through a magnetic field, inducing current
  - *Throat mic*: picks up larynx vibration directly, ignoring ambient noise
- Guitar pickup: string vibration -> electrical signal
  - Magnet + coil of wire; vibrating steel string disturbs the magnetic field, inducing current in the coil
- Speaker / headphone: electrical signal -> pressure waves (the reverse — coil in magnetic field pushes a cone)

Output signals from transducers are tiny (millivolts) because the source energy itself is tiny — voices, vibrating strings, and pressure waves carry very little power. Transducers are designed for fidelity (faithful waveform capture), not strength.

## Amplification

- Amplification = increasing a signal's amplitude while preserving its waveform.
- The shape carries the information (pitch, timbre, voice). Amplification scales the wave vertically — bigger, not different.
- The energy comes from an external power source (wall, battery), not from the input signal. The input just *controls* how that power gets shaped.
- Gain = the multiplication factor. Often expressed in decibels (dB).
- Linear amplification preserves shape exactly. Non-linear amplification distorts it (e.g., guitar overdrive when the amp clips peaks because they exceed the supply voltage).
- Universal pattern: capture cleanly, then amplify. Used in radios, guitar amps, hearing aids, scientific instruments, even radio telescopes.

## Modulation — putting information onto a carrier

To transmit a signal wirelessly, you stamp it onto a high-frequency carrier wave:

- AM (Amplitude Modulation): voice signal controls the carrier's height. WWII aircraft radios used AM.
- FM (Frequency Modulation): voice signal wiggles the carrier's frequency slightly. More noise-resistant; used in modern FM radio.

Why a carrier is needed:

1. Practical antenna sizes require high frequencies (short wavelengths)
1. Multiple conversations can share the airwaves on different carrier frequencies

The receiver does the reverse — demodulation strips the carrier away and recovers the original voice signal.

## Resonance and tuning

A resonant system has a natural frequency it "wants" to oscillate at, determined by its physical properties. It responds strongly to driving forces at that frequency, weakly to others.

- Guitar string: energy sloshes between kinetic (motion) and potential (tension). Frequency set by length, tension, mass.
- LC circuit (inductor + capacitor): energy sloshes between magnetic field (L) and electric field (C). Frequency set by L and C values: f = 1 / (2π√(LC))

Same physics, different domains. Both selectively respond to their natural frequency.

Radio tuning: the antenna picks up thousands of frequencies at once. An LC circuit tuned to one frequency builds up a strong signal at that frequency and ignores the rest. Turning the tuning knob adjusts the capacitor, changing which frequency resonates.

Q (quality factor) measures how sharp the resonance is. High Q = narrow, selective response. Low Q = broader, fuzzier response. Applies to strings (clear vs. muddy pitch) and circuits (clean vs. bleeding stations).

## Radio bands — HF vs. VHF

| Property | HF (3–30 MHz) | VHF (30–300 MHz) |
| ------------- | -------------------------------------------------- | -------------------------- |
| Behavior | Bounces off ionosphere ("skywave") | Punches through ionosphere |
| Range | Long (hundreds–thousands of miles) | Line-of-sight only |
| Reliability | Variable; affected by atmosphere, time of day, sun | Stable and predictable |
| Audio quality | Noisier, more interference | Cleaner |
| Antenna size | Large (long wavelengths) | Small (short wavelengths) |

A lot of this technology was developed during WWII for aircraft and military communication. Early radios were HF, but as the war progressed, they shifted to VHF for better clarity and reliability in combat. VHF is still the standard for voice communication in aviation and many other applications today.

## Same pattern, different domains

| System | Capture | Amplify | Output |
| --------------- | ------------ | ----------------------------- | ------------------------ |
| WWII radio | Throat mic | Tubes | Antenna / headphones |
| Electric guitar | Pickup | Tube/solid-state amp | Speaker cab |
| Phone call | Mic | DSP + transmitter | Speaker on the other end |
| Radio telescope | Antenna dish | Cooled low-noise amps | Computer / data |
| Human ear | Eardrum | Middle ear bones (mechanical) | Cochlea / brain |

The fundamental engineering pattern — transducer -> amplifier -> transmission medium -> receiver -> amplifier -> transducer — shows up everywhere once you start looking for it.
