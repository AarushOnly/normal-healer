# NormalHealer: Smart Boolean & Shading Fixer for Blender

> **1-Click artifact-free boolean cuts and instant curved surface normal healing.**

---

## 💥 The Problem
When performing Boolean cuts on curved surfaces (cylinders, spheres, pipes, automotive bodies, hard-surface models), Blender creates messy topology at the cut seam. This results in:
* **Ugly dark shading artifacts** and black pinching across the curved hull.
* **Loss of surface curvature normals**.
* **Tedious 15-step manual workarounds** (manual duplicate caching, hidden collections, Data Transfer modifier vertex loop targeting, weighted normals).
* **Blender 4.1/4.2+ "Auto Smooth" confusion** where the legacy checkbox was replaced with modifiers.

---

## ⚡ What NormalHealer Does

NormalHealer automates the entire professional hard-surface normal projection pipeline into **a single click or shortcut**:

1. **✂️ Smart Cut & Heal (`normalhealer.smart_cut`):**
   * Select your Target mesh (e.g., Cylinder) and your Cutter (e.g., Cube/Cylinder).
   * Run **Smart Cut & Heal**.
   * It creates a clean, hidden geometry reference cage parented to your target.
   * Configures a non-destructive `Data Transfer` modifier targeting split custom normals.
   * Adds a `Weighted Normal` modifier to flatten planar faces and preserve bevels.
   * Turns the cutter into a wireframe so you can move/rotate it interactively with **zero shading distortion**.

2. **🩹 Heal Existing Shading (`normalhealer.heal_existing`):**
   * Have an object that already has bad Boolean cuts? 
   * Click **Heal Existing Shading**—it automatically snapshots the pre-cut mesh and reconstructs pristine surface normals.

3. **🌊 Universal Auto-Smooth:**
   * Works seamlessly across **Blender 3.6 LTS, 4.0, 4.1, and 4.2+**.
   * Quickly smooths multiple selected objects with one click at 35° or 60°.

4. **🔍 Surface Quality Inspector:**
   * One-click toggle into a high-contrast Zebra / Reflection MatCap to visually verify surface curvature and reflection lines.

5. **💾 Bake & Purge:**
   * Ready to export your game asset or send to a 3D printer? 
   * One click applies the modifiers, bakes the custom normal data into the mesh, and purges temporary reference cages.

---

## 🚀 How to Install

### For Blender 4.2+ (Modern Extensions System):
1. In Blender, go to **Edit > Preferences > Get Extensions**.
2. Click the top-right dropdown arrow $\rightarrow$ **Install from Disk...**
3. Select `normal_healer.zip`.

### For Blender 3.6 / 4.0 / 4.1:
1. In Blender, go to **Edit > Preferences > Add-ons**.
2. Click **Install...**
3. Select `normal_healer.zip` and enable the checkbox next to **Mesh: NormalHealer**.

---

## 🎮 Shortcuts & Locations

* **Sidebar Panel:** `3D Viewport > Press 'N' > Tab: Normal Healer`
* **Quick Pie Menu:** `Shift + Alt + N` (anywhere in 3D Viewport)
* **Context Menu:** `Right-Click` any mesh in Object Mode $\rightarrow$ **Normal Healer**

---

## 📬 Author & Support

* **Developer:** Integral
* **Direct Support Email:** [integral7535@gmail.com](mailto:integral7535@gmail.com)
* **Copyright:** © 2026 Integral. Released under GPL-3.0-or-later.



---

## 📂 Project Structure

```text
normal_healer/
├── __init__.py               # Core registration, keymaps, and bl_info
├── blender_manifest.toml     # Modern Blender 4.2+ Extension manifest
├── operators.py              # Boolean cutting, normal projection, healing logic
├── ui.py                     # N-Panel, Pie Menu, and Context Menu
├── utils.py                  # Cage management, Data Transfer & smoothing helpers
└── README.md                 # Documentation
```
