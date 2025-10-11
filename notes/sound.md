# Sound

## Audio Formats

- Mono: Single channel, no spatial info
- Stereo: Left/right channels create width
- 5.1/7.1 Surround: Speakers around you (numbers = ear-level.subwoofer.height)
- Dolby Atmos: Adds height dimension with ceiling/upward-firing speakers for 3D sound
- Subwoofer: Handles low frequencies (bass/rumble), less directional so you only need one

## Setting Up Atmos at Home

What You Need:

- AV Receiver with Atmos support
- Speakers: Front L/R, Center, Surrounds, Height speakers (ceiling or upward-firing)
- Subwoofer
- Source devices (Apple TV, PS5, etc.)

Speaker Placement:

- Front L/R at 22-30° angles, ear height
- Center below/above TV
- Surrounds to sides/rear, slightly elevated
- Height speakers above listening position
- Subwoofer in corner (experiment for best bass)

Budget Expectations:

- 5.1.2: $800-$7,000 depending on quality tier
- 7.1.4: Add $400-$2,000+ for extra speakers
- Mid-range ($2,000-3,500) is the sweet spot

## Connections

- Devices (PS5, etc.) -> Receiver -> TV via HDMI
- Speakers wire directly to receiver
- One HDMI cable from receiver to TV's ARC/eARC port handles both directions:
  - Video TO TV from your devices
  - Audio FROM TV (for native apps) back to receiver

## Smart TVs

Smart TVs utilize ARC (older) or eARC (newer) cables to send & receive audio information from receivers. eARC is newer and can deliver higher quality audio than the older version.

Device Flow goes:

- PS5 -> Receiver -> TV (video only)

  - PS5 -> Receiver -> Speakers (audio)
  - The Receiver decodes audio and sends it to speakers, while passing video through to the TV

- TV Native Apps -> Receiver (via eARC) -> Speakers

  - TV generates content and sends audio back to the Receiver through the same HDMI cable (eARC), which then plays it over your speakers

Once you connect a receiver, you should:

- Disable the TV's internal speakers entirely in settings
- Set "Audio Output: External Speaker" or "Optical/HDMI"
- This prevents the TV from trying to play audio alongside your speakers (creates echo/phase issues)

## Audio vs Video Bits

Audio data is MUCH smaller than video, which is why we can stream high-quality audio more easily than high-quality video.

4K Video (Netflix, Disney+):

- ~25 Mbps (megabits per second) for 4K HDR streaming
- ~15-20 Mbps for standard 4K
- That's 25,000,000 bits per second

Dolby Atmos Audio (streaming):

- ~768 kbps (kilobits per second) via Dolby Digital Plus with Atmos
- That's 768,000 bits per second

The ratio: Video is using roughly 30-40x more bandwidth than audio.

## How Audio Is Captured

Sound is an analog waveform - continuous vibrations in air. To store it digitally, we need to convert it to numbers. This process is called sampling.

- Instead of recording a smooth curve, we're taking thousands of snapshots per second and storing the height of the wave at each moment.

Sample Rate is how many times per second the audio waveform is measured

- 44.1 kHz (CD quality) = 44,100 samples per second
- 48 kHz (DVD, streaming) = 48,000 samples per second
- 96 kHz (high-res audio) = 96,000 samples per second
- 192 kHz (audiophile territory) = 192,000 samples per second

The standard of 44.1 kHz came about because humans hear up to ~20 kHz. The Nyquist theorem says you need to sample at twice the highest frequency you want to capture.

- To capture 20 kHz audio -> sample at 40 kHz minimum
- This means we capture 44,100 audio samples / second to record sound information

Bit Depth is how precisely we measure the amplitude (volume/height) of the waveform at each sample.

- Think of it like the resolution of your measurement ruler.
- 16-bit (CD quality) = 65,536 possible volume levels (2^16)
- 24-bit (professional/streaming) = 16,777,216 possible volume levels (2^24)
- 32-bit float (recording/production) = even more precision
- What this means: at each sample point, we're saying "the wave is at level 32,451 out of 65,536 possible levels" (for 16-bit).

Adding bit depth gives more headroom for production and post-processing / editing to fix things up and improve the actual quality of the audio.

Data rate = Sample rate _ Bit depth _ Number of channels

- Sample rate: 44,100 samples/second
- Bit depth: 16 bits/sample
- Channels: 2 (left and right)
- 44,100 × 16 × 2 = 1,411,200 bits per second, or ~1.4 Mbps (megabits per second)

Adding more channels multiplies the data. Each channel is an independent audio stream that needs its own samples.

- 5.1 Surround is 6 total channels (Front L, Front R, Center, Rear L, Rear R, LFE (subwoofer))
- 48,000 (sample rate) × 24 (bit depth) × 6 (channels) = 6.912 Mbps

### Compression

The real magic comes during compression. These high Mbps numbers for uncompressed audio become significantly smaller when compressed before transmission.

Example: 12-channel Atmos

- Uncompressed: ~13.8 Mbps
- Compressed (Dolby Digital Plus): ~0.768 Mbps
- Compression ratio: ~18:1

How lossy compression works:

- Removes audio data your ears can't perceive anyway (psychoacoustic masking)
- Loud sounds mask nearby quiet sounds - we discard what you can't hear
- High/low frequencies humans are less sensitive to get fewer bits
- Result: 95% smaller file, sounds nearly identical to most listeners

This happens at the source (Netflix's servers) before streaming begins. The compressed audio travels through:

- Application Service -> ISP -> Internet -> Your Device -> Receiver -> Speakers

The tradeoff:

- Massive bandwidth savings (18x smaller)
- Imperceptible quality loss for most people
- Makes high-quality audio streaming practical on normal internet connections

Lossless alternative (Blu-ray):

- Only ~2-3:1 compression, perfect reconstruction
- ~6 Mbps instead of 0.768 Mbps
- Better quality, but 8x more bandwidth needed

Finally, Encoding is the process of converting raw audio/video into a compressed, standardized format that can be stored and transmitted efficiently.

## Pi Hole

If you have a Smart TV and want to setup Ad block, you have to opt for a network-level approach. This can be setup via Raspberry Pi device and the Pi Hole software.

- Raspberry Pi ($35-45) - Pi Zero 2 W works, but Pi 4/5 is better for performance

Pi HHole is a DNS Sinkhole for the entire home network.

- For example, when you load https://netflix.com, it asks a DNS Server "what's the IP for netflix.com?"
- Pi Hole intercepts this. Your devices ask Pi-hole for DNS lookups instead of your ISP's DNS
- Pi-hole checks if the domain is on a blocklist (ad servers, trackers, etc.)
  - If blocked, returns a null response and the ad never loads
  - If allowed, forwards the request to a real DNS server to serve the response
- It's network-wide, so every device (TV, phone, laptop, tablet) benefits automatically.

### Pi Hole Setup

1. Install Raspberry Pi OS

- Download Raspberry Pi Imager software to your computer
- Flash the OS onto the microSD card
- Enable SSH for remote access (checkbox in the imager)

2. Boot and Connect

- Insert microSD into Pi, plug in power and ethernet
- Find the Pi's IP address (check your router's admin page)

3. Install Pi-hole

- SSH into the Pi from your computer
- Run one command: `curl -sSL https://install.pi-hole.net | bash`
- Follow the setup wizard (takes ~10 minutes)
- It'll give you an admin password and web interface URL

4. Configure Your Router

- Log into your router's admin panel
- Change the DNS server setting from automatic to your Pi's IP address
- All devices on your network now use Pi-hole for DNS

This then is setup at http://pi.hole/admin where you can see real time queries, what's being blocked, or add more custom domains + blocklists

- Run `pihole -up` every few months to get bug fixes, security pattches, new features
