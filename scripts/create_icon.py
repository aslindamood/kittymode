"""Generate simple cat icons for the application."""
import os
from pathlib import Path

from PIL import Image, ImageDraw


def create_cat_icon(size: int, output_path: str) -> Image.Image:
    """Create a simple cat face icon.
    
    Args:
        size: Icon size in pixels
        output_path: Path to save the PNG
        
    Returns:
        The created image
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Scale factor
    s = size / 64
    
    # Cat face color (purple-ish)
    color = (147, 112, 219)
    outline = (100, 70, 180)
    
    # Head (circle)
    draw.ellipse([int(8*s), int(16*s), int(56*s), int(60*s)], fill=color, outline=outline)
    
    # Left ear
    draw.polygon([
        (int(8*s), int(24*s)), 
        (int(16*s), int(4*s)), 
        (int(24*s), int(20*s))
    ], fill=color, outline=outline)
    
    # Right ear
    draw.polygon([
        (int(40*s), int(20*s)), 
        (int(48*s), int(4*s)), 
        (int(56*s), int(24*s))
    ], fill=color, outline=outline)
    
    # Inner ears (pink)
    pink = (255, 182, 193)
    draw.polygon([
        (int(12*s), int(22*s)), 
        (int(16*s), int(10*s)), 
        (int(20*s), int(20*s))
    ], fill=pink)
    draw.polygon([
        (int(44*s), int(20*s)), 
        (int(48*s), int(10*s)), 
        (int(52*s), int(22*s))
    ], fill=pink)
    
    # Eyes (white with black pupils)
    draw.ellipse([int(18*s), int(30*s), int(28*s), int(42*s)], fill='white')
    draw.ellipse([int(36*s), int(30*s), int(46*s), int(42*s)], fill='white')
    draw.ellipse([int(21*s), int(34*s), int(26*s), int(40*s)], fill='black')
    draw.ellipse([int(39*s), int(34*s), int(44*s), int(40*s)], fill='black')
    
    # Nose (pink triangle)
    draw.polygon([
        (int(32*s), int(42*s)), 
        (int(28*s), int(48*s)), 
        (int(36*s), int(48*s))
    ], fill=pink)
    
    # Mouth
    draw.arc([int(24*s), int(46*s), int(32*s), int(54*s)], 0, 180, fill='black', width=max(1, int(s)))
    draw.arc([int(32*s), int(46*s), int(40*s), int(54*s)], 0, 180, fill='black', width=max(1, int(s)))
    
    image.save(output_path)
    return image


def create_ico(output_path: str) -> None:
    """Create Windows .ico with multiple sizes.
    
    Args:
        output_path: Path to save the ICO file
    """
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    assets_dir = Path(output_path).parent
    
    for size in sizes:
        img = create_cat_icon(size, str(assets_dir / f'icon_{size}.png'))
        images.append(img)
    
    # Save as ICO
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )


def create_icns(output_path: str) -> None:
    """Create macOS .icns (simplified - just create PNGs).
    
    For proper icns, use iconutil on macOS.
    Here we create the required PNG sizes.
    
    Args:
        output_path: Path for the icns (PNGs created alongside)
    """
    assets_dir = Path(output_path).parent
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        create_cat_icon(size, str(assets_dir / f'icon_{size}x{size}.png'))
    
    print(f"Created PNG icons. To create .icns on macOS, run:")
    print(f"  iconutil -c icns assets/icon.iconset")


def main():
    """Generate all icon files."""
    # Find project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    assets_dir = project_root / 'assets'
    
    assets_dir.mkdir(exist_ok=True)
    
    print(f"Creating icons in {assets_dir}...")
    
    create_ico(str(assets_dir / 'icon.ico'))
    print("Created assets/icon.ico")
    
    create_icns(str(assets_dir / 'icon.icns'))
    print("Created PNG icons for macOS")


if __name__ == '__main__':
    main()
