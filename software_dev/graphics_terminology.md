# DirectX
Graphics API developed by Microsoft for use on the Windows OS
- Allows programs to access your computer's hardware in a lightweight manner.
- Allows hardware independence so lots of different computers w/ different components can use the same API
- Gives developers an interface to build graphics for their game and allows them to have confidence that most machines will be able to run it
- Games typically install DirectX on your machine so that they can guarantee everything will work fine.
- Direct3D is one of the tools that DirectX encompasses.  There are multiple others.

# Vulkan
Cross Platform Graphics API.  Newer than OpenGL.
- Every graphics card can use it
- Can be used on any Platform such as Windows, Mac, Linux etc
- Built to overcome inefficiencies of previous low level GPU APIs (OpenGL)
- Theoretically the most efficient platform to build on, but if developers implement things poorly then ya DirectX could potentially run better

# OpenGL
Graphics API used by developers to build graphics software
- Talks directly to your GPU
- Competitor to DirectX and Vulkan
- Much less verbose than Vulkan, so probably better for smaller projects

# DXVK
Open Source project that provides a Vulkan-based implementation of Direct3D 9, 10, 11 which allows for running DirectX games on Linux through Wine.
- It's a low level language that can talk directly to the GPU because it's built via Vulkan, so there isn't much overhead for all the programming calls
- This provides better performance and compatability compared to the default Wine Direct3D Implementation.
- Reduces CPU Usage and improves overall stability during gaming.
- Helps enable better graphics rendering, especially on modern GPUs
- Included on multiple 3rd party launchers like Bottles, Lutris etc.
