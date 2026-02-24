# Ray Tracing

## What Is Ray Tracing

Ray tracing is a rendering technique that simulates the physical behavior of light to generate images. It works by tracing the path of light rays as they interact with objects in a virtual scene, calculating how light bounces, refracts, reflects, and gets absorbed by surfaces. The result is photorealistic imagery with accurate shadows, reflections, refractions, and global illumination.

Ray tracing has been used in offline rendering (film, architecture, product visualization) for decades, but only recently became feasible for real-time applications like video games due to hardware acceleration.

## How Ray Tracing Works

### The Core Idea

In the real world, light sources emit photons that bounce around a scene until some reach your eyes. Simulating this directly (forward tracing) is computationally wasteful because the vast majority of photons never reach the camera. Ray tracing inverts this: it casts rays backward from the camera through each pixel of the image plane into the scene, then traces how those rays interact with geometry and materials.

### Step-by-Step Process

1. **Ray generation**: For each pixel, one or more primary rays are cast from the camera origin through the image plane into the scene.

1. **Intersection testing**: Each ray is tested against scene geometry to find the nearest object it hits. This is the most computationally expensive step and relies heavily on acceleration structures (typically Bounding Volume Hierarchies, or BVHs) to avoid brute-force testing against every triangle.

1. **Shading**: At the intersection point, the material properties of the surface are evaluated. Depending on the material, several secondary rays may be spawned:

   - **Shadow rays** are cast toward light sources to determine if the point is in shadow.
   - **Reflection rays** are cast in the mirror direction for reflective surfaces.
   - **Refraction rays** pass through transparent materials (glass, water) according to Snell's law.
   - **Diffuse/indirect rays** are cast in random directions to capture indirect illumination (light bouncing off other surfaces).

1. **Recursion**: Secondary rays repeat the intersection and shading process, potentially spawning more rays. A maximum recursion depth (bounce limit) prevents infinite loops.

1. **Color accumulation**: The final pixel color is computed by combining contributions from all ray paths, weighted by material properties, light falloff, and probability distributions.

### Acceleration Structures

Without optimization, ray tracing is O(n) per ray where n is the number of primitives. Acceleration structures reduce this dramatically:

- **BVH (Bounding Volume Hierarchy)**: A tree of axis-aligned bounding boxes that recursively subdivide scene geometry. Traversal is O(log n) per ray. This is the dominant structure in modern ray tracers and what GPU hardware accelerates.
- **KD-Trees**: Space-partitioning trees that split along axis-aligned planes. Slightly better traversal performance than BVH in some cases but harder to build and update for dynamic scenes.
- **Uniform/Hierarchical Grids**: Divide space into cells. Simple to build but inefficient for scenes with non-uniform geometry distribution.

## Variants of Ray Tracing

### Whitted Ray Tracing (Classical)

The original approach from Turner Whitted (1980). Handles perfect specular reflections, refractions, and hard shadows. Does not handle diffuse interreflection (color bleeding, soft indirect light). Relatively cheap because it only spawns a small number of deterministic secondary rays.

### Path Tracing

A Monte Carlo method that stochastically samples the full rendering equation. At each bounce, a single (or small number of) random direction is chosen rather than deterministically spawning reflection/refraction rays. Given enough samples per pixel, path tracing converges to a physically correct solution. This is the standard in film production rendering (used by Pixar's RenderMan, Arnold, Cycles, etc.). The tradeoff is noise at low sample counts, requiring hundreds or thousands of samples per pixel for clean images.

### Bidirectional Path Tracing

Traces paths from both the camera and the light sources, then connects them. More efficient than unidirectional path tracing for scenes with complex light transport (caustics, small light sources illuminating through narrow openings).

### Metropolis Light Transport (MLT)

Uses Markov chain Monte Carlo to explore light paths. Particularly effective for difficult lighting scenarios like light passing through a crack under a door. Rarely used in real-time contexts.

### Photon Mapping

A two-pass algorithm. First, photons are emitted from light sources and stored where they hit surfaces (building a photon map). Second, camera rays are traced and the photon map is queried to estimate illumination. Good for caustics and participating media (fog, smoke).

## Ray Tracing vs. Rasterization

Rasterization is the traditional real-time rendering approach used in games and interactive applications. Understanding the differences is essential.

### Rasterization Overview

Rasterization works object-by-object rather than pixel-by-pixel. For each triangle in the scene, it projects the triangle onto the screen and fills in the covered pixels. It determines visibility via a depth buffer (z-buffer). Lighting and shading are computed per-vertex or per-pixel using approximations.

### Comparison

| Aspect | Rasterization | Ray Tracing |
| ----------------------- | --------------------------------------------------- | -------------------------------------------- |
| Approach | Project geometry onto screen | Cast rays from camera into scene |
| Reflections | Screen-space approximations (SSR), cube maps | Physically accurate, recursive |
| Shadows | Shadow maps, cascaded shadow maps | Naturally accurate via shadow rays |
| Global illumination | Baked lightmaps, screen-space methods, light probes | Naturally handled via indirect rays |
| Transparency/Refraction | Sorted alpha blending, approximations | Physically correct via refraction rays |
| Ambient occlusion | Screen-space AO (SSAO, HBAO, GTAO) | Naturally emerges from path tracing |
| Performance | Very fast, highly parallelizable on GPUs | Orders of magnitude more expensive per frame |
| Image quality ceiling | Limited by approximation accuracy | Converges to ground truth |
| Off-screen effects | Cannot reflect/shadow objects not visible to camera | Handles off-screen geometry naturally |

### Where Rasterization Falls Short

Rasterization fundamentally operates in screen space, meaning it can only work with what is currently visible to the camera. This creates several categories of artifacts:

- Reflections of off-screen objects are missing (screen-space reflections fail at edges).
- Shadow maps have resolution limits, causing aliasing (shadow acne, peter-panning).
- Global illumination must be precomputed or faked, making dynamic lighting difficult.
- Transparent objects require careful sorting and still produce artifacts.

### Where Ray Tracing Falls Short

- Massively more compute per frame. A single frame of a Pixar film can take hours to render.
- Real-time ray tracing requires aggressive denoising at low sample counts, which can introduce its own artifacts (ghosting, loss of detail).
- Memory bandwidth requirements are high due to incoherent memory access patterns (rays go everywhere, unlike rasterization's predictable access).

## Real-Time Ray Tracing

### Hardware Acceleration

NVIDIA introduced dedicated ray tracing hardware (RT cores) with the Turing architecture (RTX 2000 series, 2018). AMD followed with RDNA 2 (RX 6000 series, 2020). Intel's Arc GPUs (Alchemist, 2022) also include ray tracing units. These cores accelerate BVH traversal and ray-triangle intersection testing in dedicated fixed-function hardware, providing a massive speedup over software ray tracing.

### APIs

- **DirectX Raytracing (DXR)**: Microsoft's API extension for DirectX 12. Provides ray generation shaders, intersection shaders, closest-hit shaders, miss shaders, and any-hit shaders.
- **Vulkan Ray Tracing**: Khronos Group's cross-platform equivalent, based on the VK_KHR_ray_tracing_pipeline extension.
- **OptiX**: NVIDIA's proprietary ray tracing SDK, widely used in professional visualization and offline rendering.
- **Metal Ray Tracing**: Apple's ray tracing API for their GPU family, available on M-series chips and recent AMD GPUs in Macs.

### Hybrid Rendering

Almost no current game uses pure ray tracing for the full image. The standard approach is hybrid rendering: rasterization handles primary visibility (determining what object each pixel sees), and ray tracing handles specific effects selectively:

- **RT Reflections**: Replace screen-space reflections for accurate mirror/glossy surfaces.
- **RT Shadows**: Replace shadow maps for pixel-perfect soft shadows from area lights.
- **RT Global Illumination**: Compute indirect lighting via traced rays rather than precomputed lightmaps. Examples include RTXGI, Lumen (Unreal Engine 5).
- **RT Ambient Occlusion**: Replace SSAO with traced short-range occlusion rays.

### Denoising

At real-time sample rates (often 1 sample per pixel or fewer), raw ray-traced images are extremely noisy. Denoisers are critical:

- **Temporal accumulation**: Reuse shading results from previous frames, reprojected to the current frame. Effective but causes ghosting on fast-moving objects.
- **Spatial filtering**: Blur the noisy signal using edge-aware filters that preserve geometric boundaries (bilateral filters, a-trous wavelets).
- **AI/ML denoising**: NVIDIA's DLSS Ray Reconstruction and similar techniques use neural networks trained on pairs of noisy/clean images to reconstruct high-quality output from sparse samples.

### Performance Scaling

Current real-time ray tracing performance depends heavily on ray budget. Typical costs in a modern game frame:

- Primary rays (rasterized): effectively free via rasterization.
- RT reflections: 0.5 to 1 ray per pixel for glossy surfaces.
- RT shadows: 1 ray per pixel per light source.
- RT GI: 0.25 to 1 ray per pixel, heavily denoised.

Total ray budgets in current games are typically 1 to 4 rays per pixel per frame, compared to the hundreds or thousands needed for clean offline rendering.

## Other Rendering Alternatives

### Radiosity

A finite-element method that solves diffuse interreflection by subdividing surfaces into patches and computing energy transfer between them. Produces soft, realistic indirect lighting for diffuse scenes but cannot handle specular reflections. Was popular in the 1990s for architectural visualization. Largely superseded by path tracing and irradiance caching methods.

### Screen-Space Techniques

A collection of post-processing methods that operate on the rasterized G-buffer (depth, normals, albedo):

- SSAO/HBAO/GTAO for ambient occlusion
- SSR for reflections
- SSGI for approximate global illumination

These are fast and widely used but fundamentally limited by the screen-space constraint (no information about occluded or off-screen geometry).

### Signed Distance Fields (SDF) / Ray Marching

Instead of testing rays against triangle meshes, ray marching steps along a ray using a distance field that encodes the closest surface at any point in space. Used heavily in demoscene and creative coding (Shadertoy). Unreal Engine 5 uses software-based SDF tracing for its Lumen global illumination system at lower quality levels. SDFs are compact and support smooth blending of shapes, but representing detailed geometry accurately requires very high resolution fields or clever composition.

### Neural Radiance Fields (NeRF) and Gaussian Splatting

Emerging techniques that represent scenes as learned functions (NeRF) or collections of oriented Gaussians (3DGS). They can produce photorealistic novel views from captured photographs. Currently more relevant to view synthesis and reconstruction than traditional real-time rendering, but the boundary is blurring as these techniques become faster and more controllable.

## The Current Landscape and Future Direction

Fully path-traced games are starting to appear. Titles like Cyberpunk 2077 (with RT Overdrive mode), Portal RTX, and Quake II RTX demonstrate full path tracing in real-time, though they require high-end hardware and rely heavily on DLSS/FSR upscaling and denoising.

The trajectory is clear: as GPU hardware improves and denoising techniques mature, the industry is moving toward replacing more rasterization-based approximations with ray-traced equivalents. The end goal is real-time path tracing as the default rendering pipeline, eliminating the need for the many layered hacks (shadow maps, reflection probes, lightmaps, SSAO) that define current rasterization pipelines.

Key trends to watch include hardware ray tracing performance scaling per generation, neural denoising and reconstruction quality, software-based ray tracing approaches (like Lumen) that work without dedicated RT hardware, and the convergence of traditional rendering with neural/learned representations.
