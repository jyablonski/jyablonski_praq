# Boss Katana Settings

## 1. Drop D / Strat Settings

_This creates the main rhythm "roar." We use high volume and lower gain to maintain punch._

- Amp Type: `BROWN`
- Gain: `55 - 60` (Lower gain = tighter palm mutes)
- Volume: `65` (Sets the relative volume of this preset)
- Bass: `75` (Drop tunings need a massive low-end foundation)
- Middle: `85` (Crucial: Tool is mid-forward, not scooped)
- Treble: `60`
- Presence: `60 - 65` (High enough for bite, low enough to cut digital "fizz")
- Cab Resonance: `MODERN` (Tightens the low-end)

## 2. Booster (The "Tightening" Agent)

_Crucial Step: Used as a "clean boost" to cut mud before the amp._

- Switch: `ON` (Always)
- Type: `T-SCREAM` (Tube Screamer) or `OVERDRIVE`
  - Models the famous green Ibanez TS808 pedal.
  - This pedal has a built-in "EQ Curve" that naturally cuts bass and boosts mids. It is the industry standard for tightening metal guitars. It makes the palm mutes go "CHUG" instead of "BOOM."
- Drive: `0`
  - This means we are not adding distortion via the booster, just tightening the signal.
- Tone: `+5 to +10` (Right of center)
  - The EQ. Turning this up makes the signal brighter before distortion. This adds "teeth" or "pick attack" to the sound. If this is too low, the guitar sounds like it's under a blanket.
- Effect Level: `100` (Max)
  - The Volume. This is the most important knob. By maxing this, we are slamming the front of the amp with a super loud signal. The amp reacts by compressing more and sustaining longer.
- Direct Mix: `0`
  - The Blend. This mixes your clean, dry guitar signal back in with the effect. For metal, we want this at 0. We want 100% of the signal to be processed by the booster so all the mud is cut. If you turn this up, you'll hear clean "plinking" underneath your distortion.

Drop D tuning produces a lot of low-frequency "flab." If you send that "flab" straight into a high-gain amp, the amp gets overwhelmed and sounds muddy (like a blown speaker).

The "Tightening" Mechanism Explained Simply: When you down-tune to Drop D (or lower), your strings become "floppier" and vibrate much wider. This dumps a huge amount of sub-bass frequencies (the "flub") into the amp right away. Adding boost:

- Acts as a pre-filter, cutting the low end before it hits the amp. If we feed booming bass into a distortion circuit, it chokes and sounds messy.
- Boosts the mids which is the most important frequency range for this style of music.
- Increases the overall signal level going into the amp, causing it to compress and sustain more.

If you turn the boost off and try palm muting, it'll sound "boomy" and undefined. With the boost on, palm mutes are tight and punchy.

## 3. Effects (Texture & Space)

- Modulation (Flanger 117E): `OFF` by default.
  - _Settings:_ Rate `5`, Depth `60`, Regen `0-10` (Keep regen low to stop the "jet plane" swoosh).
- Delay (Digital/Tape): `OFF` by default.
  - _Settings:_ Time `420ms - 500ms`, Feedback `30`, Level `25`.
- Reverb (Plate): `ON` (Subtle).
  - _Settings:_ Time `1.2s`, Low Cut `165Hz`, High Cut `4.00kHz` (Dark, metallic studio room).

## 4. Utility / "Pro" Tweaks

- Noise Suppressor (NS): `ON`. Threshold `30`, Release `15` (Fast release for tight stops).
- Parametric EQ: `OFF`. (Your core tone is already good; don't strangle it).

______________________________________________________________________

## 5. How to Set Your Guitar (Crucial)

- Pickup Selector: Position 1 (Bridge Humbucker).
  - _Why:_ The only pickup that handles high gain without hum/noise.
- Tone Knob: 10 (Max).
  - _Why:_ Feed the amp the clearest signal possible. Distortion compresses the sound; if you cut treble here, the amp sounds muffled.
- Volume Knob: 10 (Max).
  - _Why:_ Max signal = Max gain/chug.

## 6. How to Control Volume (The Rules)

- Power Control (Physical Knob): Set to 0.5W.
  - _Why:_ Allows you to push the Master Volume higher for better tone without shaking the walls.
- Guitar Volume: Leave at 10.
  - _Exception:_ Roll down to 3-4 to clean up the sound for quiet verses.
- Amp Channel Volume: Leave at ~65.
- Master Volume: ADJUST FREELY.
  - _Why:_ This is your monitor level. It changes _loudness_ but does not change _tone_. Use this to match the volume to your room.

## Drop B / Schecter Settings

### 1. The "Hidden" Preamp (Active Pickups)

With EMGs, your guitar has its own preamp inside it (that’s why it needs a 9V battery).

- What this changes: You are sending a signal that is _already_ compressed, boosted, and EQ-shaped before it even hits the cable.
- The Benefit: You don't need to "fake" the aggression with the Booster Drive knob anymore. The guitar is doing the heavy lifting.

### 2. The Amp (Scooped & Sharp)

- Amp Type: `LEAD` (Switch from "Brown").
  - _Why:_ The "Lead" channel on Katana is more modern and fizzy/sharp
- Gain: `80-85` (High, but don't max it. The EMGs are pushing it hard already).
- Bass: `80-85` (Massive low end).
- Mids: `35` (THE KEY CHANGE).
  - _Why:_ Slipknot is "Scooped." You remove the "body" to make it sound cold, metallic, and machine-like.
- Treble: `75` (Compensates for the lack of mids).
- Presence: `65-75` (Adds "sizzle" to the pick attack).

#### B. The Booster (Still Essential)

Even with EMGs, you still need the Booster for Drop B to tighten the low end.

- Type: `T-SCREAM` (Still the best for tightening).
- Drive: `0` (Keep it at zero - Your EMGs are already distorted enough. Adding drive here creates feedback).
- Tone: `+10` (Max brightness for attack).
- Level: `100`.

#### C. The Noise Gate (CRITICAL)

EMGs are quiet, but with `Gain 80` + `Booster` + `Lead Channel`, the amp will scream when you stop playing.

- Threshold: Crank this up to `50` or `60`.
- Release: `0 - 5` (Instant stop). You want silence the millisecond you mute the string.

## Sound Signal Chain

`Input (Guitar)` -> `NS (Detection)` -> `Booster` -> `Distortion (Preamp)` -> `Amp EQ` -> `Reverb` -> `Power Amp (Presence)` -> `Master Volume`

______________________________________________________________________

### 1. Input: The Source (Guitar)

- Settings: Bridge Humbucker, Volume 10, Tone 10.
- Action: Sends the raw, unmodified signal.
- Why: We need maximum signal strength here. If you cut tone/volume now, you are feeding the amp weak data. We want the amp to have "full clay" to sculpt with.

### 2. Noise Suppressor: The Gatekeeper (Detection)

- Location: Detects signal at the Input, acts on the noise later.
- Action: It watches your guitar strings.
  - Moving? "Open the gate!" (Let sound through).
  - Stopped? "Slam the gate shut!" (Mute everything instantly).
- Why: High gain creates a loud hum (hiss). Without this, when you stop playing a riff, the amp would hiss feedback at you. This makes the silence between notes dead quiet.

### 3. The Booster: The Tightener (Pre-Distortion)

- Location: Before the distortion.
- Action: We use the pedal (Tube Screamer) to CUT the bass and BOOST the mids.
- Why: We are feeding the distortion engine. If we feed it a "fat" bass signal (Drop D), the engine chokes and sounds muddy. We starve it of bass so it distorts cleanly and tightly.

### 4. The Gain: The Engine (Preamp)

- Location: The core of the preamp.
- Action: It takes that "thin/tight" signal from the booster and amplifies it until it clips (distorts).
- Result: Because the input was lean, the distortion texture is "crunchy" and "defined" rather than "farty."

### 5. The Amp EQ: The Body Builder (Post-Distortion)

- Location: After the distortion is already created.
- Action: This is where your `Bass: 75` and `Mids: 85` settings live.
- Why: Now that we have a clean, tight distortion texture, we can use the Bass knob to make it loud and heavy.
- The Magic: Because the distortion has _already happened_, adding bass here doesn't make it muddy. It just makes that tight crunch sound massive.

### 6. Effects: The Atmosphere (Reverb)

- Location: Near the end of the chain.
- Action: Adds a subtle "Plate" echo to the sound.
- Why: If you put reverb _before_ distortion, it sounds like a mess. Placing it here ensures the "echo" is clean and sits _behind_ the heavy guitar, creating that dark "studio room" feel without washing out the riff.

### 7. Presence: The Polish (Power Amp)

- Location: The very end of the tone-shaping (Power Amp section).
- Action: Controls the "sizzle" and "air" of the speakers.
- Why: This is the final filter.
  - Too Low: Sound is blanketed/dull.
  - Too High: Sound is fizzy/digital.
  - Just Right (65): It cuts the digital fizz but keeps the aggressive "bite" of the pick attack.

### 8. Master Volume: The Monitor (Output)

- Location: The final knob before the real world.
- Action: Controls the physical volume of the speaker.
- Why: This knob is transparent. It does not change the tone, the gain, or the distortion. It simply takes the finished tone we built in steps 1-7 and decides how loud to play it.
