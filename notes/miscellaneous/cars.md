# Car Engine Components & How They Work

## Complete Flow

1. Battery provides electrical power to the starter motor
1. Starter motor turns the crankshaft to start the engine
1. Crankshaft rotates and drives the camshaft via the timing chain
1. Camshaft opens and closes the intake and exhaust valves in sync with the pistons
1. Air is drawn through the air intake, past the throttle body, which controls how much air enters the engine based on driver input
1. Air-fuel mixture enters the cylinders during the intake stroke
1. Spark plugs ignite the mixture during the power stroke, creating combustion
1. Combustion forces the pistons down, generating power to turn the crankshaft
1. Flywheel attached to the crankshaft helps smooth out power delivery and maintain momentum between combustion cycles
1. Crankshaft sends power to the clutch (manual) or torque converter (automatic), which connects and disconnects the engine from the transmission
1. Transmission adjusts torque and speed depending on the gear (lower gears = more torque for acceleration, higher gears = more speed for cruising)
1. Power is sent through the driveshaft to the differential, which splits power between the left and right wheels while allowing them to spin at different speeds during turns. The differential also applies the final drive ratio, multiplying torque one last time before it reaches the wheels.
1. Axles (half-shafts) carry the rotation from the differential to the wheel hubs, propelling the car forward.

Extra components:

- Alternator: Generates electricity to recharge the battery and power electrical systems while the engine is running
- Throttle body: Houses a butterfly valve that regulates airflow into the intake manifold. In modern cars it's electronically controlled (drive-by-wire) by the ECU based on accelerator pedal position
- Fuel injectors: Spray fuel into the intake air stream for precise control of the air-fuel mixture
- Fuel pump: Pressurizes fuel from the tank and delivers it to the injectors at the required pressure
- Ignition coil: Steps up battery voltage to the tens of thousands of volts needed to fire the spark plugs
- ECU: Computer that manages fuel injection, ignition timing, throttle position, and other parameters for optimal performance and efficiency
- Sensors: Mass airflow sensor, oxygen sensors, crankshaft and camshaft position sensors, knock sensor, coolant temperature sensor, and others feed real-time data to the ECU so it can adjust fueling and timing
- Lubrication system: Oil pump circulates oil through the engine via galleries and the oil filter to reduce friction and wear on moving parts
- Cooling system / Radiator: Water pump circulates coolant through the engine block and radiator, with a thermostat regulating temperature
- Exhaust system: Carries burnt gases away from the cylinders, through the catalytic converter (which reduces harmful emissions), and out the muffler (which dampens the sound of those rapid-fire pressure waves from combustion). An oxygen sensor in the exhaust stream lets the ECU fine-tune the air-fuel ratio
- Air intake system: Filters and directs air into the engine through the air filter, then past the mass airflow sensor and throttle body into the intake manifold, which distributes air evenly to each cylinder
- PCV system: Positive Crankcase Ventilation routes blow-by gases from the crankcase back into the intake to be re-burned, reducing emissions and pressure buildup
- Engine mounts: Rubber or hydraulic mounts that secure the engine to the chassis while isolating vibration
- Forced induction (if equipped): Turbocharger (driven by exhaust gases) or supercharger (driven by the crankshaft) compresses intake air to cram more into the cylinders, increasing power. Usually paired with an intercooler to cool the compressed air before it enters the engine

## The Four-Stroke Cycle

This is the fundamental process that powers your engine. Each cylinder goes through these four steps:

1. Intake Stroke

- The camshaft opens the intake valve
- The piston moves downward, creating a vacuum
- Air-fuel mixture is pulled into the cylinder
- The intake valve closes

2. Compression Stroke

- Both valves are now closed
- The piston moves upward
- The air-fuel mixture is compressed into a smaller space
- This compression makes the combustion more powerful

3. Power Stroke

- The spark plug ignites the compressed mixture at the top
- The explosion forces the piston downward
- This is the stroke that generates power to move the car

4. Exhaust Stroke

- The camshaft opens the exhaust valve
- The piston moves upward again
- Burnt gases are pushed out of the cylinder
- The exhaust valve closes and the cycle repeats

Key fact: The crankshaft rotates twice (720 degrees) to complete one full four-stroke cycle.

This cycle happens many times per second across all cylinders, creating the continuous power that propels your car. It takes less than 200 ms for all 4 cylinders to complete a full cycle at 3,000 RPM.

- The flywheel helps smooth out the power delivery by storing rotational energy during the power stroke and releasing it between strokes, preventing the engine from stalling and providing momentum to keep the crankshaft spinning.

An engine stall is basically the crankshaft slowing down so much that the flywheel can't carry it through to the next power stroke. Mainly only a problem in manual transmission cars if you let the RPMs drop too low while in gear, or if you release the clutch too quickly without enough throttle. In an automatic, the torque converter helps prevent stalling by allowing some slippage at low speeds.

## Major Engine Components

### Camshaft

- Controls the opening of intake and exhaust valves
- Has specially shaped lobes ("cams") that push valves open
- Rotates once for every two rotations of the crankshaft
- Springs automatically close the valves after the cam pushes them open

### Crankshaft

- Converts the up-and-down motion of pistons into rotational motion
- Connected to pistons via connecting rods
- Drives the camshaft through the timing belt/chain
- Provides the rotating power that eventually turns the wheels

### Timing Chain/Belt

- Connects the crankshaft to the camshaft
- Ensures they rotate in perfect synchronization
- Timing chain (like in your 2012 Sonata): metal, lasts the life of the engine, no replacement needed
- Timing belt: rubber, needs replacement every 60k-100k miles or it can break and cause catastrophic damage

### Throttle/Gas Pedal

- Controls airflow into the engine via the throttle valve
- More air in = more fuel automatically added by fuel injectors
- Engine computer maintains optimal air-fuel ratio (about 14.7:1)
- More air-fuel mixture = bigger combustions = more power

### Pistons

- Move up and down inside cylinders
- Connected to the crankshaft via connecting rods
- Compress the air-fuel mixture and receive the force from combustion

### Valves

- Intake valves: let air-fuel mixture into the cylinder
- Exhaust valves: let burnt gases out of the cylinder
- Controlled by the camshaft, closed by springs

## Forced Induction: Turbochargers & Superchargers

Both turbochargers and superchargers are devices that force more air into the engine than it could normally breathe on its own. More air means more fuel can be added, resulting in bigger combustions and significantly more power without increasing engine size.

### Turbocharger

How it works:

- Uses exhaust gases to spin a turbine
- The turbine is connected to a compressor via a shaft
- As hot exhaust gases exit the engine, they spin the turbine at extremely high speeds (up to 150,000+ RPM)
- The compressor on the other side compresses incoming air and forces it into the engine
- Essentially recycles waste energy from the exhaust to create more power

Advantages:

- More power from a smaller engine (better fuel efficiency when not boosting)
- No direct drain on engine power (uses waste exhaust gases)
- Can produce very high power levels

Disadvantages:

- "Turbo lag" - slight delay between pressing the gas and getting boost (turbine needs time to spin up)
- More complex with additional components (intercooler, wastegate, etc.)
- Generates significant heat
- More maintenance requirements

Common features:

- Intercooler: cools the compressed air before it enters the engine (cooler air is denser = more oxygen)
- Wastegate: releases excess exhaust pressure to prevent over-boosting and damage
- Boost pressure typically measured in PSI (pounds per square inch)

### Supercharger

How it works:

- Mechanically driven by the engine's crankshaft via a belt
- Spins a compressor that forces air into the engine
- Provides instant boost as soon as you press the throttle (no lag)
- Common types: roots-type, twin-screw, centrifugal

Advantages:

- Instant throttle response (no turbo lag)
- Boost is proportional to engine RPM - very predictable power delivery
- Simpler installation than turbochargers
- Distinctive whine sound (especially roots-type superchargers)

Disadvantages:

- Takes power from the engine to drive the compressor (parasitic loss)
- Typically less efficient than turbochargers
- Less effective at high altitudes compared to turbos

Power trade-off:

- Uses about 20-30% of the power it creates to drive itself
- Still results in a net gain of power, but not as efficient as a turbo using "free" exhaust energy

### Key Comparisons

| Feature | Turbocharger | Supercharger |
| ----------------- | ---------------------------------- | ------------------------------- |
| Power source | Exhaust gases | Engine crankshaft (belt-driven) |
| Throttle response | Delayed (turbo lag) | Instant |
| Efficiency | More efficient (uses waste energy) | Less efficient (parasitic drag) |
| Complexity | More complex | Simpler |
| Heat generation | Very high | Moderate |
| Power delivery | Can be abrupt | Linear and predictable |
| Maintenance | Higher | Lower |

### Why Forced Induction Matters

Power without displacement:

- A turbocharged 2.0L engine can produce as much power as a naturally aspirated 3.5L engine
- This is why many modern cars use smaller turbocharged engines ("downsizing")

Altitude compensation:

- At high altitudes, naturally aspirated engines lose power because the air is thinner
- Turbos can compensate by forcing more air in, maintaining power at elevation

Performance tuning:

- Boost levels can often be adjusted to increase power output
- This is why turbocharged cars are popular in the tuning/modification community

### Common Terminology

- Boost: The amount of pressure (PSI) the turbo/supercharger creates above atmospheric pressure
- Spool: The process of a turbo building boost (turbine spinning up to speed)
- Blow-off valve (BOV): Releases compressed air when you let off the throttle (prevents compressor surge)
- Wastegate: Controls boost pressure by releasing excess exhaust gases
- Intercooler: Heat exchanger that cools compressed air before it enters the engine

## Power Delivery System

### Front-Wheel Drive (FWD) Setup

Crankshaft -> Transaxle -> Axles -> Front Wheels

Transaxle: Combines transmission and differential in one unit

- Transmission part: changes gears to balance speed vs torque
- Differential part: splits power between two wheels, allows them to rotate at different speeds when turning

Axles (CV axles/half-shafts): Two short shafts that connect the transaxle to each front wheel

- Have CV joints at both ends to flex with suspension and steering
- Only the front wheels receive power; rear wheels just roll freely

### Rear-Wheel Drive (RWD) Setup

Crankshaft -> Transmission -> Driveshaft -> Differential -> Axles -> Rear Wheels

## Transmission & Gears

### Purpose

Adjusts the balance between torque (pulling power) and speed to match driving conditions.

### Lower Gears (1st, 2nd, 3rd)

- High torque, low speed
- Used for: starting from a stop, accelerating, climbing hills
- Small gear on engine side drives large gear on wheel side
- Engine revs high but wheels turn slowly with lots of force

### Higher Gears (4th, 5th, 6th)

- Low torque, high speed
- Used for: highway cruising at constant speed
- Gear ratio closer to 1:1 or reversed
- Engine revs low while wheels turn fast
- Maximum fuel efficiency, less engine wear

### Why Higher Gears Are Better for Cruising

- Lower RPMs = fewer combustion cycles per minute
- Less fuel consumption
- Less engine wear
- Quieter, smoother ride
- You already have momentum, so you don't need much torque to maintain speed

## Key Measurements

### RPM (Revolutions Per Minute)

- How many times the crankshaft completes a full rotation per minute
- Higher RPM = more combustion cycles = more power but also more fuel use and wear
- Each combustion cycle requires 2 crankshaft rotations
- Example: 3,000 RPM = 1,500 combustion cycles per minute per cylinder

### Air-Fuel Ratio

- Optimal ratio: approximately 14.7 parts air to 1 part fuel
- Engine computer automatically adjusts fuel to match incoming air
- You control air (via throttle), computer controls fuel

## Maintenance Notes for Your 2012 Hyundai Sonata

- Timing chain: No replacement needed (lasts life of engine)
- Oil changes: Every 5,000-7,500 miles
- Serpentine/accessory belt: Check around 60,000 miles
- TPMS sensors: Can be replaced/fixed during next tire change
- General maintenance: Consult owner's manual for complete schedule

## Wheel Horsepower

There are 2 different types of horsepower measurements for cars:

1. Crank horsepower is the advertising number: It's what manufacturers publish, and while it's a real measurement, it's done at the engine in isolation, not in the actual car. It represents the theoretical maximum output before any of it has to fight through the drivetrain.

1. Every gas car loses power between the engine and the wheels: This is unavoidable physics. Any mechanical system has friction, and any time you transfer rotational energy through gears, fluids, and bearings, some of it becomes heat instead of motion. There's no such thing as a 100% efficient drivetrain. Even race cars with the most optimized drivetrains lose some power, just less than a typical street car.

1. A chassis dyno gives you the real wheel horsepower number: It measures what's actually being delivered to the road. This is the true performance number, accounting for everything between the engine and pavement.

EVs have much less drivetrain loss because of fewer moving parts and a more direct power delivery, which is why their wheel horsepower is often much closer to their motor's rated horsepower.

## Hybrids

Hybrid cars combine an internal combustion engine with one or more electric motors. The electric motor can assist the engine for better fuel efficiency and performance, and in some cases can power the car on its own for short distances (like in a plug-in hybrid). The battery is charged through regenerative braking and sometimes by plugging in. Hybrids are designed to optimize fuel economy while still providing the benefits of a traditional gasoline engine when needed.

There are multiple types of hybrids:

1. Mild Hybrid: Uses a small electric motor to assist the engine, but can't run on electricity alone. It provides better fuel efficiency and smoother start-stop operation.
1. Full Hybrid: Can run on the engine, the electric motor, or a combination of both. It can drive short distances on electric power alone, making it more efficient in stop-and-go traffic. Cannot be plugged in; the battery is charged through regenerative braking and engine use.
1. Plug-in Hybrid: Can be plugged in to charge the battery, allowing for longer electric-only driving ranges. Combines the benefits of a full hybrid with the ability to drive significant distances on electric power alone. Can be driven indefinitely on gas alone if you never plug it in, but the electric mode is where you get your moneys worth.

### Battery Charging

Hybrid batteries can be charged through a few ways:

1. Gas engine often generates more power than the car needs, so some of this is routed to a generator to charge the battery. Engine can also fire up to charge the battery, instead of typical propulsion use.
1. Regenerative braking captures kinetic energy when you slow down and converts it into electricity to recharge the battery. This is why hybrids feel different when you lift off the gas pedal - they use that opportunity to slow the car and recharge the battery at the same time.
1. Plug-in hybrids can be charged by plugging into an external power source, allowing for longer electric-only driving ranges.

Hybrid batteries charge by themselves and require 0 maintenance. They're designed to last the life of the car.

Plug-ins can be charged on regular 120V outlets, but it'll take longer than using a dedicated 240V charger. The electricity cost is about the same regardless of the charging method, 240V is just faster.
