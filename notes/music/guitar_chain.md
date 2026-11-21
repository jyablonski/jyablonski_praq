# Guitar Signal Chain

`Guitar → pedals → preamp → effects loop → power amp → speaker cabinet → mic`

## Analog Signal Chain

- **Pickup and cable.** A vibrating string changes the magnetic field at the pickup and induces a voltage in its coil. A bridge pickup emphasizes upper harmonics relative to the fundamental, so it sounds brighter than a neck pickup. A passive pickup, its controls, and the cable form a resonant filter. More cable capacitance usually moves that resonance lower. An early buffer helps preserve treble through the cables that follow it. Put pickup-sensitive vintage fuzzes before the buffer.
- **Before the preamp.** Wah, compression, EQ, boost, and overdrive shape what hits the amp’s gain stages. A Tube Screamer-style boost with low drive and higher level trims bass and pushes mids, which helps palm mutes stay defined. EQ before distortion changes which frequencies drive the clipping. EQ after distortion shapes the resulting tone.
- **Preamp.** The preamp supplies most of the distortion in a high-gain amp. The tone stack shapes the frequency balance, and its position varies by design.
- **Effects loop.** The loop typically sits between the preamp and power amp. Delay, reverb, and chorus in the loop stay more distinct when the preamp is dirty. Move delay before the preamp for more smeared repeats. A volume pedal before the preamp can clean up the drive. In the loop it controls level after that distortion.
- **Power amp.** A power amp can compress or clip when pushed. In some amps the supply voltage dips under load, producing the softer attack called sag. The speaker’s impedance changes with frequency, which can shape a tube amp’s low-end punch and treble response. Presence and resonance controls often adjust the high and low ends of that response through feedback. With two physical cabs, check that the amp supports their combined impedance.
- **Speaker, cab, and mic.** Guitar speakers roll off much of the harsh top end. Closed-back cabs tend to sound punchier and more directional. Open-back cabs spread sound behind the amp. Aim a close mic toward the dust cap for more bite or toward the cone edge for a darker sound. Moving a directional mic closer can add bass. A close mic also picks up less room sound than you hear standing in front of the cab.

## Quad Cortex

- **Input.** Leave headroom for your hardest pick attack. Clipping at the input carries through the preset.
- **Amp model or Neural Capture.** A native amp model gives you controls for adjusting the virtual amp. A Neural Capture learns how a particular rig responds around the settings used to make it. For a very different gain or EQ setting, try another capture. A capture made with a mic on the cab already includes that speaker and mic sound.
- **Cab or IR Loader.** The Cab block has movable virtual mics. The IR Loader uses imported impulse responses. A static cab IR recreates the frequency and timing response of a speaker, cab, and mic at a fixed position. Speaker compression and breakup that change with level require separate modeling or a capture that includes them.
- **Monitoring.** Add cab simulation to an amp-only model or capture for headphones, a PA, studio monitors, or a full-range, flat-response (FRFR) speaker. To play through a real guitar cab, send the amp-only signal to a power amp or an amp’s effects return. Headphones give you the mic’s perspective. A guitar cab in the room adds off-axis sound and room reflections.
- **Recording.** Save both the processed tone and a dry DI track over USB. The DI lets you reamp the same performance through a different preset later.

## Blending Cabs on the Quad Cortex

| Setup | Routing |
| --- | --- |
| Two mics on one factory cab | Enable both mic slots in one Cab block. Set position, level, and polarity for each. |
| Two imported IRs | Use a Double IR Loader. Adjust each IR’s level, pan, polarity, and delay. |
| Two factory cabs | Split after the Amp block, put a Cab block on each path, and blend them with a Mixer. |
| Two amp and cab paths | Split before the amp blocks so each path has its own gain and speaker voicing. |

Center two mono paths for a mono blend. Pan them apart for stereo width from one performance. For double-tracked rhythms, record the part twice and pan the two takes.

If the blend sounds hollow, listen in mono and check timing and polarity. Two equal copies offset by 1 ms cancel at 500 Hz, 1.5 kHz, and 2.5 kHz, among other frequencies. This is comb filtering. The Phase switch flips polarity. To align imported IRs, use the IR Loader’s Delay control on the earlier side.

1. Dial in one cab or mic on its own. Add a quieter second voice, such as a ribbon mic under an SM57 or a Greenback under a Vintage 30.
1. Match the output level when comparing one cab with the blend. Sum both sides to mono to preview a mono PA or speaker.
1. If the blend needs cleanup, try a low cut around 80 Hz and a high cut around 8–10 kHz after blending. Adjust both in the mix.
