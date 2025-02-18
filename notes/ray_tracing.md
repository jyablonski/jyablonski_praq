# Ray Tracing

### **Ray Tracing vs. Rasterization: A Deeper Look**

#### **Ray Tracing: Physically Accurate Light Simulation**  
Ray tracing is a rendering technique that **simulates the physics of light** to create highly realistic images. It works by tracing the path of light rays as they travel through a scene, interacting with objects by reflecting, refracting, and casting shadows—just like in the real world.  

#### **Why Ray Tracing is Computationally Expensive**  
- Instead of directly "drawing" objects on the screen, ray tracing **simulates** how light moves and interacts with materials.  
- Each pixel on the screen requires shooting out multiple rays, which then bounce around the scene, potentially hitting multiple objects and requiring further calculations.  
- This recursive bouncing (for reflections, refractions, global illumination) makes it incredibly demanding on hardware.  
- To make real-time ray tracing feasible, modern GPUs (like NVIDIA RTX and AMD Radeon RX 6000+ series) use **dedicated RT cores** to accelerate these calculations.  

##### **Pros of Ray Tracing**  
✔ Realistic lighting, reflections, shadows  
✔ Natural-looking ambient occlusion & global illumination  
✔ Handles complex interactions like caustics (e.g., light bending through glass or water)  

##### **Cons of Ray Tracing**  
❌ Extremely computationally expensive  
❌ Even with modern GPUs, real-time ray tracing requires **upscaling techniques** like DLSS (Deep Learning Super Sampling) to maintain performance  
❌ Harder to optimize for real-time applications  

---

#### **Rasterization: Faster, Approximate Rendering**  
Rasterization, on the other hand, **does not** simulate light physics. Instead, it is a much more optimized approach that converts 3D objects into 2D pixels (fragments) as efficiently as possible.  

##### **How Rasterization Works**  
1. **Vertex Processing** – 3D models made of triangles are projected onto a 2D screen.  
2. **Z-Buffering** – The GPU determines which triangles are visible (handling occlusion).  
3. **Shading & Texturing** – Lighting is applied using **simplified models** (e.g., Phong shading, normal maps, baked lighting) instead of simulating real light.  
4. **Screen-Space Effects** – Effects like reflections and ambient occlusion are done in **post-processing** rather than being physically simulated.  

##### **Pros of Rasterization**  
✔ Much faster than ray tracing, making it ideal for real-time rendering (video games, VR, etc.)  
✔ Well-optimized hardware (GPUs are built for rasterization)  
✔ Can still produce highly realistic results with clever techniques (e.g., baked lighting, screen-space reflections, shadow mapping)  

##### **Cons of Rasterization**  
❌ Doesn't simulate light physics accurately  
❌ Screen-space reflections (SSR) break down when reflections aren’t visible on screen  
❌ Shadows and lighting need **tricks** like shadow maps and baked lighting to look convincing  

---

### **Why Ray Tracing is the Future (But Rasterization Still Matters)**
- **Ray tracing is more realistic, but computationally expensive** – modern GPUs still struggle to run it in real time.  
- **Hybrid rendering** (mixing rasterization and ray tracing) is becoming common in modern games (e.g., Cyberpunk 2077, Control).  
- **Rasterization is still the dominant method for games** because of its efficiency.  
- **Ray tracing is used in movies and pre-rendered content** (e.g., Pixar movies) where real-time performance isn’t a concern.  

In short: **Rasterization is a "good enough" hack for real-time rendering, while ray tracing is the long-term goal for photorealistic visuals** but requires way more power.
