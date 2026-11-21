# Guitar Effects

**Dry** is the signal going into an effect. **Wet** is the signal the effect adds or produces. **Mix** blends the two.

## Gain and Dynamics

| Effect | What it does |
| --- | --- |
| Clean boost | Raises the signal level without intentionally clipping. Before a driven amp it adds saturation. After the drive stages it can add volume if there’s headroom. |
| Overdrive | Adds clipping, usually with some pick dynamics intact. A Tube Screamer-style drive trims bass and emphasizes mids. Low Drive and higher Level can tighten palm mutes into a high-gain amp. |
| Distortion | Adds denser clipping and compression. Use it for a sustained, more saturated sound into a clean or lightly driven amp. |
| Fuzz | Produces a coarse, buzzy sound. Some fuzzes sputter as notes decay. Pickup-sensitive vintage fuzzes usually work best before a buffer. |
| Compressor | Turns down peaks so soft and loud notes sit closer together. Makeup gain can make the tail of a note more audible. Use a slower attack to keep more pick snap. |
| Noise gate | Attenuates the signal below a threshold. Set it high enough to quiet idle noise and low enough to keep soft notes. Put it before delay and reverb so their tails can ring out. |
| Volume pedal | Makes swells or lets you adjust level with your foot. Before drive it changes how hard you hit the gain stage. After drive it mainly changes loudness. |

A compressor’s **threshold** sets when it starts working. **Ratio** sets how strongly it compresses above that point. **Attack** and **release** control how quickly it clamps down and lets go.

## Amp and Cabinet

- **Amp.** The preamp shapes gain and overdrive. The power amp drives the speaker and can add compression or clipping when pushed. On a modeler, start with Gain for saturation and use the output or channel Level to match loudness across presets.
- **Cab.** The speaker and cabinet shape the sound coming out of the amp. A cab sim or impulse response (IR) typically includes a mic perspective. A position near the speaker center usually sounds brighter than one near the cone edge. Use cab simulation with an amp-only model into headphones, monitors, or a PA.

## EQ

EQ changes the level of different frequencies. **Before distortion**, it changes what drives the clipping. **After distortion**, it shapes the finished tone.

| EQ type | What you control |
| --- | --- |
| Amp tone stack | Bass, Mid, and Treble make broad changes. On many amps the controls interact, so adjusting one also changes how the others respond. |
| Graphic | Boost or cut fixed frequency bands with sliders. Quick for broad changes, such as bringing back mids that disappear in a mix. |
| Parametric | Set the center frequency, gain, and width of each adjustable band. **Q** controls width. Higher Q means a narrower band. |
| Semi-parametric | Usually lets you choose frequency and gain with a fixed bandwidth. |
| Dynamic | Boosts or cuts a band in response to signal level. Useful for dialing back low-end boom that shows up only on hard palm mutes. |

**Filter shapes** tell you what the band affects. A **bell** targets a region around its center frequency. A **shelf** raises or lowers one end of the spectrum. A **high-pass** (low cut) rolls off lows. A **low-pass** (high cut) rolls off highs. A **tilt** brightens one end of the spectrum while darkening the other.

## Modulation, Filters, and Pitch

| Effect | What you hear |
| --- | --- |
| Chorus | A thicker, gently wavering sound from mixing the dry signal with a slightly delayed copy whose pitch shifts. |
| Flanger | A metallic sweep from mixing in a very short delay that changes over time. More feedback makes the sweep more pronounced, up to a jet-like sound. |
| Phaser | A rounded, swirling sweep. It shifts phase by different amounts at different frequencies, then blends the result with the dry signal to create moving dips. |
| Vibrato | Pitch rises and falls around the note, giving it a wobble. |
| Tremolo | Volume rises and falls in a pulse. Deeper settings can make the sound chop in and out. |
| Wah | A foot pedal sweeps a resonant filter for the vowel-like sound. An envelope filter can sweep with picking intensity. |
| Pitch shifter or octave | Moves a copy of the note up or down in pitch. An octave below adds weight to single notes. An octave above gives leads a brighter edge. |

On most modulation effects, **Rate** sets the speed and **Depth** sets the amount of movement. Start with both low for subtle motion.

## Delay and Reverb

- **Delay** makes distinct repeats. **Time** sets the gap, **Feedback** sends some of the repeat back through the delay for more repeats, and **Mix** sets their level relative to the dry signal. Digital delay can give clear repeats. Analog delay tends to darken as it repeats. Tape-style delay can add softening and pitch wobble. For slapback, try one short repeat around 100 ms.
- **Reverb** simulates a space or a resonant surface. **Room** adds a short sense of space, **hall** gives a longer tail, **plate** has a smooth, dense tail, and **spring** has a metallic bounce. **Decay** sets tail length. **Pre-delay** creates a gap before the reverb, which helps the dry note stay distinct.

## Starting Chains

These are starting points for a modeler. With a physical amp, try delay and reverb in the effects loop when using the amp’s preamp distortion.

- **Tight rhythm** `Overdrive → high-gain amp → cab → EQ`. Start with low Drive on the overdrive. Try a low cut if the cab sound booms, or a gate if noise fills the gaps between notes.
- **Swirling clean** `Compressor → clean amp → cab → slow phaser or flanger → short plate`. Keep modulation depth and reverb mix low so the chords stay clear.
- **Lead** `Overdrive → amp → cab → delay → reverb`. Use a few quiet repeats and a short plate. For a volume lift, raise the output level after the gain stages.

Match levels when comparing two settings. Change one effect at a time and listen with the rest of the track.
