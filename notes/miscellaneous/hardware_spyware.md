# Hardware as a Spyware/Adware Delivery Channel

Consumer hardware: monitors, prebuilt PCs, and smart TVs increasingly ships or auto-fetches software whose purpose is advertising, bundleware promotion, or data collection rather than device function. This is driven by thin hardware margins and lucrative software/data revenue, and it persists because the legal and technical incentives all point toward "do it, with disclosure."

## Two distinct categories (often conflated)

1. Bounty/bundleware — Trial software (e.g. McAfee, Norton) pre-installed or auto-installed. The OEM is paid per install and per conversion. Annoying, but usually not covert tracking.
1. Data monetization — Actual telemetry: viewing habits, usage patterns, sold to advertisers/data brokers. This is the smart-TV model, and the one consumers would object to most.

## How it works — the Windows loophole

- Windows has a Plug-and-Play feature that queries connected hardware and auto-fetches a matching vendor "companion app" from the Store.
- In the recent case, plugging in LG UltraGear monitors caused Windows to silently install an "LG Monitor App Installer," whose first visible act was a McAfee trial promotion.
- Alienware (AWCC) and Asus (Armoury Crate) ride the same mechanism; some reinstall after removal because the hardware keeps re-triggering the fetch.
- Key point: the OEM often isn't hand-installing malware — it's exploiting a sanctioned OS convenience feature. Microsoft built the rails.

## How it works — the TV loophole

- Smart TVs run Automatic Content Recognition (ACR): the set fingerprints on-screen content and reports what you watch.
- That data is sold to advertisers and brokers. Vizio settled with the FTC over exactly this.
- Economics: the TV is sold near cost and monetized over its lifetime via ads and data — the data business can out-earn the hardware.

## OEM motivation

- Hardware margins are thin (often single digits), so software placement fees are near-pure profit that subsidizes the sticker price.
- Bounty deals are a cheaper customer-acquisition channel for the software vendor than buying ads — and free money for the OEM.
- For TVs/phones, recurring ad + data revenue can exceed one-time hardware profit entirely.

## What the software vendors (McAfee/Norton) get

- The pre-install is the top of a subscription funnel. First-year economics are intentionally negative.
- Profit comes from auto-renewal at ~3–4x the promo price; roughly 60–70% of promo buyers renew at full price at least once.
- The model is engineered around inertia: free trials, auto-renewal, invisible renewal charges, high cancellation friction.
- Norton's parent (Gen Digital) treats basic security as a funnel to upsell higher-margin identity/privacy bundles. (Ironically, its Avast unit was FTC-banned in 2024 for selling browsing data — the "protection" software was the tracker.)

## Why the legal/security teams greenlight it

- Consent is manufactured via buried ToS language: a silent practice becomes a contractual one the moment you click "agree."
- Risk is asymmetric: BD/finance capture certain revenue; security/legal carry diffuse, probabilistic downside.
- US enforcement is slow and penalties are survivable relative to revenue (Vizio, Lenovo Superfish both happened and were absorbed).
- Superfish is the cautionary line — Lenovo's adware broke HTTPS and became a real vulnerability. Most bundleware is compartmentalized specifically to stay a nag screen, not a breach.

## Mitigations

- Windows: disable "download manufacturer apps and info" under device installation settings, or via Group Policy, to block the auto-fetch.
- TVs: turn off ACR (named "Viewing Information Services," "Live Plus," etc. depending on brand).
- General: buy multi-year retail licenses over auto-renew subs; audit startup apps and Reliability Monitor after new hardware.

## Why it won't stop on its own — the incentive equilibrium

The pattern has run 20+ years under rotating brand names. That longevity isn't a series of accidents; it's what a stable, profitable equilibrium looks like. Every party with the power to end it is worse off if it ends.

Defaults are decisions. Microsoft has had two decades and vast engineering resources, yet the hardware auto-fetch ships *enabled by default*. A company that repeatedly picks the complaint-generating default over the user-protecting one is revealing a preference, not maintaining a legacy quirk. "It's just a convenience feature" stops explaining anything once the fix is trivial and still isn't shipped.

Who benefits from the status quo:

- Security vendors: cheap top-of-funnel, profit on renewals.
- OEMs: per-install/conversion bounties offset thin margins.
- Microsoft: a compliant OEM ecosystem + its own ads-in-Windows business; no incentive to close the door, and it hasn't.
- Users: pay in attention, bloat, forgotten renewals, and (in the data-harvesting layer) exfiltrated data.

Alignment without collusion. There's no single conspiracy — it's three self-interested business models stacked through a Windows feature nobody with power has reason to remove. That's *harder* to dislodge than a cartel, because there's no agreement to break up.

Distinguish the two harms, because the remedy differs:

- *Adware/bounties* extract money and attention. Killed by pre-install disclosure rules and default-off mandates.
- *Data harvesting* (TV ACR, "protection" apps that were the trackers — see Avast/Jumpshot) extracts data without meaningful consent. Killed only by privacy law with teeth: opt-in consent, data-broker limits, and enforcement that costs more than the revenue.
- Conflating them lets each industry point at the other. Keeping them separate is what makes either fixable.

Bottom line: This persists not because it's hard to stop but because stopping it is adverse to the interests of everyone able to stop it. The beneficiaries are concentrated and incentive-aligned; the harmed are diffuse, uninformed, and don't switch. Real leverage sits outside the market — regulation that makes non-consensual collection cost more than it pays — plus individual defenses (kill the auto-fetch, disable ACR, avoid auto-renew) that remove *you* from the funnel without changing the system.
