# TAGGER / photo_tagging

A local, personal photo-tagging tool for organizing your photography library. TAGGER provides a simple desktop GUI (built with Tkinter) to manage photo tags, inspect shooting parameters, and store an index locally.

> **Note:** TAGGER only deletes its **index records** and **thumbnail cache**. It **never** deletes your original photo files.

---

## Features

- Import local photo files (common image formats supported)
- Automatically read capture time and common EXIF metadata:
  - Camera body, lens, focal length, shutter speed, ISO, and more
- Generate thumbnails automatically and browse them in a grid
- Multi-select photos and apply tags in bulk
- Quickly filter photos by:
  - **Untagged**
  - **A specific tag**
- Open photo details via double-click
- Right-click actions:
  - Remove a photo record from the local index
  - Remove a tag globally
- Configurable focal length display mode:
  - Off
  - Always ×1.5
  - Auto (detected by camera body when possible)

---

## Getting the Project

You can obtain the project using either method below:

### 1) Clone with Git (recommended)

```bash
git clone https://github.com/gracezhouxinyuan/photo_tagging.git
cd photo_tagging
