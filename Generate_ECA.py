import ECA as eca
import numpy as np
import os
import sys
import argparse

# randbstr randomly generates a binary string of input length.
def randbstr(stringlength):
    rng = np.random.default_rng()
    key = ''
    for i in range(stringlength):
        temp = str(rng.integers(1, endpoint = True))
        key += temp
    return key

# initcentercell returns binary string with a single 1 in the center,
# taking as input the number of zeroes on either side of the 1.
def initcentercell(numZeroes):
    key = ''
    for i in range(numZeroes):
        key += '0'
    key += '1'
    for i in range(numZeroes):
        key += '0'
    return key

# Visualize the cellular automata data using ASCII or a simple custom renderer
def visualize_eca(data, mode="ascii", downsample=4, output_file=None, boundary='periodic', rule=None):
    height, width = len(data), len(data[0])
    
    if mode == "ascii":
        # ASCII visualization (▓ for 1, space for 0)
        output = ""
        for row in data:
            line = ""
            for i in range(0, len(row), downsample):
                if row[i] == 1:
                    line += "▓"
                else:
                    line += " "
            output += line + "\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Output saved to {output_file}")
        else:
            print(output)
    
    elif mode == "html":
        # HTML visualization (creates a simple HTML file with colored cells)
        html = """<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 0; background: #f0f0f0; }
  .container { margin: 20px auto; width: fit-content; }
  .grid { 
    display: flex;
    flex-direction: column;
    line-height: 0;
  }
  .row {
    display: flex;
    height: 2px;
  }
  .cell0 { 
    width: 2px; 
    height: 2px; 
    background-color: white; 
    margin: 0;
    padding: 0;
  }
  .cell1 { 
    width: 2px; 
    height: 2px; 
    background-color: black; 
    margin: 0;
    padding: 0;
  }
</style>
</head>
<body>
<div class="container">
<div class="grid">
"""
        # Process the data row by row
        for row_idx, row in enumerate(data):
            html += '<div class="row">\n'
            for i in range(0, len(row), downsample):
                cell_class = "cell1" if row[i] == 1 else "cell0"
                html += f'<div class="{cell_class}"></div>'
            html += '</div>\n'
        
        html += "</div></div></body></html>"
        
        if not output_file:
            output_file = "eca_visualization.html"
        
        with open(output_file, 'w') as f:
            f.write(html)
        print(f"Visualization saved to {output_file}")
        
        # Try to open the HTML file in browser
        try:
            import webbrowser
            webbrowser.open('file://' + os.path.realpath(output_file))
        except:
            pass
    
    elif mode == "ppm":
        # Generate a simple PPM image file (P3 format)
        if not output_file:
            output_file = "eca_visualization.ppm"
        
        with open(output_file, 'w') as f:
            # PPM header
            f.write(f"P3\n{width // downsample} {height}\n255\n")
            
            # Write pixel data
            for row in data:
                for i in range(0, len(row), downsample):
                    if row[i] == 1:
                        f.write("0 0 0 ")  # Black for 1
                    else:
                        f.write("255 255 255 ")  # White for 0
                f.write("\n")
        
        print(f"PPM image saved to {output_file}")

    elif mode == "3d" and boundary == 'periodic':
        # 3D visualization (creates a HTML file with Three.js for cylindrical view)
        if not output_file:
            output_file = "eca_visualization_3d.html"
        
        # Get downsampled dimensions
        ds_width = width // downsample
        ds_height = height
        
        # Prepare data for 3D
        cylindrical_data = []
        for row in data:
            cylindrical_row = []
            for i in range(0, len(row), downsample):
                cylindrical_row.append(1 if row[i] == 1 else 0)
            cylindrical_data.append(cylindrical_row)
        
        # Create the HTML with Three.js
        html = """<!DOCTYPE html>
<html>
<head>
    <title>ECA Cylindrical Visualization</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
        canvas { width: 100%; height: 100% }
        #controls {
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.7);
            padding: 10px;
            border-radius: 5px;
            z-index: 100;
        }
        #info {
            position: fixed;
            bottom: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.7);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
        }
        button {
            margin: 2px;
            padding: 5px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        button:active {
            background-color: #3e8e41;
        }
        .active {
            background-color: #e74c3c;
        }
        .active:hover {
            background-color: #c0392b;
        }
        .color-control {
            margin-top: 8px;
        }
        .color-label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
        }
        .separator {
            margin-top: 10px;
            border-top: 1px solid #ccc;
            padding-top: 10px;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
</head>
<body>
    <div id="controls">
        <button id="zoomIn">Zoom In</button>
        <button id="zoomOut">Zoom Out</button>
        <button id="rotateLeft">Rotate Left</button>
        <button id="rotateRight">Rotate Right</button>
        <button id="toggleCylinder">Wireframe Cylinder</button>
        
        <div class="separator">
            <div class="color-control">
                <label class="color-label" for="cell1Color">1 Cell Color:</label>
                <input type="color" id="cell1Color" value="#000000">
            </div>
            
            <div class="color-control">
                <label class="color-label" for="cell0Color">0 Cell Color:</label>
                <input type="color" id="cell0Color" value="#ffffff">
                <div style="font-size: 10px; margin-top: 3px;">(0 cells are hidden by default)</div>
            </div>
            
            <div class="color-control">
                <label style="font-size: 12px;">
                    <input type="checkbox" id="renderZeroCells"> Show 0 Cells
                </label>
            </div>
            
            <button id="applyColors" style="margin-top: 8px; width: 100%;">Apply Colors</button>
        </div>
    </div>
    
    <div id="info">
        <div>Rule: RULE_NUMBER</div>
        <div>Boundary: periodic (cylindrical)</div>
        <div>Generations: GEN_COUNT</div>
        <div>Width: CELL_WIDTH</div>
    </div>
    <script>
        // ECA data
        const ecaData = CELL_DATA;
        const width = ecaData[0].length;
        const height = ecaData.length;
        
        // Color settings
        let cell1Color = "#000000";  // Black for 1 cells
        let cell0Color = "#ffffff";  // White for 0 cells
        let renderZeroCells = false; // Whether to render 0 cells
        
        // Initialize color pickers
        document.getElementById('cell1Color').value = cell1Color;
        document.getElementById('cell0Color').value = cell0Color;
        document.getElementById('renderZeroCells').checked = renderZeroCells;
        
        // Three.js setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f0f0);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            preserveDrawingBuffer: true
        });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // Controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.25;
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(1, 1, 1).normalize();
        scene.add(directionalLight);
        
        // Calculate dimensions
        const cellSize = 1;
        const cylinderRadius = (width * cellSize) / (2 * Math.PI);
        const cylinderHeight = height * cellSize;
        
        // Create a group to hold all cell objects
        const cylinderGroup = new THREE.Group();
        scene.add(cylinderGroup);
        
        // References to cylinders
        let wireCylinder = null;
        let solidCylinder = null;
        let cell1Material = null;
        let cell0Material = null;
        let cellObjects = { '0': [], '1': [] };  // Store references to cell objects by type
        
        // Convert hex color to THREE.Color
        function hexToThreeColor(hex) {
            return new THREE.Color(hex);
        }
        
        // Create individual cells for each data point
        function createScene() {
            // Clear existing cells
            while(cylinderGroup.children.length > 0) { 
                cylinderGroup.remove(cylinderGroup.children[0]); 
            }
            
            // Reset cell object references
            cellObjects = { '0': [], '1': [] };
            
            // Create materials with current colors
            cell1Material = new THREE.MeshLambertMaterial({ 
                color: hexToThreeColor(cell1Color)
            });
            
            cell0Material = new THREE.MeshLambertMaterial({ 
                color: hexToThreeColor(cell0Color)
            });
            
            // Create 3D cubes for cells
            const boxGeometry = new THREE.BoxGeometry(cellSize, cellSize, cellSize * 0.5);
            
            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    const cellValue = ecaData[y][x];
                    
                    // Skip 0 cells if not rendering them
                    if (cellValue === 0 && !renderZeroCells) continue;
                    
                    // Choose material based on cell value
                    const material = cellValue === 1 ? cell1Material : cell0Material;
                    const cube = new THREE.Mesh(boxGeometry, material);
                    
                    // Calculate position on cylinder surface
                    const angle = (x / width) * Math.PI * 2;
                    cube.position.x = Math.sin(angle) * cylinderRadius;
                    cube.position.z = Math.cos(angle) * cylinderRadius;
                    cube.position.y = (height / 2) - y;
                    
                    // Rotate cube to face outward from cylinder center
                    cube.rotation.y = angle;
                    
                    // Add to the scene and store reference by cell type
                    cylinderGroup.add(cube);
                    cellObjects[cellValue].push(cube);
                }
            }
            
            // Create a wireframe cylinder
            const wireGeometry = new THREE.CylinderGeometry(
                cylinderRadius, cylinderRadius, cylinderHeight, 
                Math.min(width, 72), Math.min(height, 36), true
            );
            const wireMaterial = new THREE.MeshBasicMaterial({ 
                color: 0xaaaaaa, 
                wireframe: true,
                transparent: true,
                opacity: 0.3
            });
            wireCylinder = new THREE.Mesh(wireGeometry, wireMaterial);
            wireCylinder.visible = showWireframe;
            cylinderGroup.add(wireCylinder);
            
            // Create a solid cylinder with double-sided rendering for complete opacity
            // First layer - inner facing
            const innerGeometry = new THREE.CylinderGeometry(
                cylinderRadius, cylinderRadius, cylinderHeight, 
                Math.min(width, 72), Math.min(height, 36), true
            );
            const innerMaterial = new THREE.MeshBasicMaterial({ 
                color: 0xeeeeee,  // Light gray
                wireframe: false,
                transparent: false,
                side: THREE.BackSide  // Only render inside of cylinder
            });
            const innerCylinder = new THREE.Mesh(innerGeometry, innerMaterial);
            innerCylinder.visible = !showWireframe;
            cylinderGroup.add(innerCylinder);
            
            // Second layer - outer facing for complete opacity
            const outerGeometry = new THREE.CylinderGeometry(
                cylinderRadius, cylinderRadius, cylinderHeight, 
                Math.min(width, 72), Math.min(height, 36), true
            );
            const outerMaterial = new THREE.MeshBasicMaterial({ 
                color: 0xeeeeee,  // Light gray
                wireframe: false,
                transparent: false,
                side: THREE.FrontSide  // Render outside of cylinder
            });
            solidCylinder = new THREE.Mesh(outerGeometry, outerMaterial);
            solidCylinder.visible = !showWireframe;
            cylinderGroup.add(solidCylinder);
        }
        
        // Update cell colors without recreating the entire scene
        function updateCellColors() {
            // Update material colors
            if (cell1Material) {
                cell1Material.color = hexToThreeColor(cell1Color);
            }
            
            if (cell0Material) {
                cell0Material.color = hexToThreeColor(cell0Color);
            }
            
            // For 0 cells, need to handle visibility based on renderZeroCells
            cellObjects['0'].forEach(cell => {
                cell.visible = renderZeroCells;
            });
        }
        
        // Position camera
        camera.position.set(0, cylinderHeight / 2, cylinderRadius * 3);
        camera.lookAt(0, cylinderHeight / 2, 0);
        
        // Handle window resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        // Control buttons
        document.getElementById('zoomIn').addEventListener('click', () => {
            camera.position.z *= 0.9;
        });
        
        document.getElementById('zoomOut').addEventListener('click', () => {
            camera.position.z *= 1.1;
        });
        
        document.getElementById('rotateLeft').addEventListener('click', () => {
            cylinderGroup.rotation.y -= Math.PI / 12;
        });
        
        document.getElementById('rotateRight').addEventListener('click', () => {
            cylinderGroup.rotation.y += Math.PI / 12;
        });
        
        // Toggle cylinder visibility
        let showWireframe = true;
        const cylinderButton = document.getElementById('toggleCylinder');
        
        cylinderButton.addEventListener('click', () => {
            showWireframe = !showWireframe;
            if (wireCylinder) wireCylinder.visible = showWireframe;
            if (solidCylinder) solidCylinder.visible = !showWireframe;
            cylinderButton.textContent = showWireframe ? "Solid Cylinder" : "Wireframe Cylinder";
            cylinderButton.classList.toggle('active');
        });
        
        // Color controls
        document.getElementById('applyColors').addEventListener('click', () => {
            // Get values from color pickers
            cell1Color = document.getElementById('cell1Color').value;
            cell0Color = document.getElementById('cell0Color').value;
            renderZeroCells = document.getElementById('renderZeroCells').checked;
            
            // If toggling 0 cell visibility, we need to recreate the scene
            if (renderZeroCells !== (cellObjects['0'].length > 0)) {
                createScene();
            } else {
                // Just update colors
                updateCellColors();
            }
        });
        
        // Initial creation
        createScene();
        
        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        
        animate();
    </script>
</body>
</html>
"""
        # Replace placeholders with actual data
        html = html.replace('RULE_NUMBER', str(rule if rule is not None else 'N/A'))
        html = html.replace('GEN_COUNT', str(ds_height))
        html = html.replace('CELL_WIDTH', str(ds_width))
        html = html.replace('CELL_DATA', str(cylindrical_data))
        
        with open(output_file, 'w') as f:
            f.write(html)
        print(f"3D visualization saved to {output_file}")
        
        # Try to open the HTML file in browser
        try:
            import webbrowser
            webbrowser.open('file://' + os.path.realpath(output_file))
        except:
            pass
    
    elif mode == "3d" and boundary != 'periodic':
        print("3D cylindrical visualization is only available with periodic boundary conditions.")
        print("Please use --boundary periodic for 3D visualization.")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Elementary Cellular Automaton Generator')
    
    # Required arguments
    parser.add_argument('--rule', type=int, required=True, help='Rule number (0-255)')
    parser.add_argument('--generations', type=int, required=True, help='Number of generations')
    
    # Optional arguments with defaults
    parser.add_argument('--boundary', type=str, default='periodic', choices=['periodic', 'null'], 
                        help='Boundary condition (periodic or null)')
    parser.add_argument('--init', type=str, default='random', choices=['random', 'center', 'custom'], 
                        help='Initial state type')
    parser.add_argument('--width', type=int, default=100, help='Width for random or center init')
    parser.add_argument('--custom', type=str, help='Custom initial state (binary string)')
    parser.add_argument('--mode', type=str, default='ascii', choices=['ascii', 'html', 'ppm', '3d'], 
                        help='Visualization mode')
    parser.add_argument('--downsample', type=int, default=1, help='Downsample factor')
    parser.add_argument('--output', type=str, help='Output file name (optional)')
    
    args = parser.parse_args()
    
    # Validate rule number
    if not (0 <= args.rule <= 255):
        print("Error: Rule must be between 0 and 255.")
        sys.exit(1)
    
    # Generate rule binary representation
    rules = np.empty(256, dtype='U8')
    for x in range(256):
        rules[x] = np.binary_repr(x, 8)
    
    # Create ECA with specified rule
    myrule = eca.ECA(rules[args.rule])
    
    # Generate initial state
    if args.init == 'random':
        initial_state = randbstr(args.width)
    elif args.init == 'center':
        initial_state = initcentercell(args.width // 2)
    elif args.init == 'custom':
        if not args.custom:
            print("Error: Custom initial state must be provided with --custom")
            sys.exit(1)
        # Validate custom input
        if not all(c in '01' for c in args.custom):
            print("Error: Custom initial state must contain only 0s and 1s")
            sys.exit(1)
        initial_state = args.custom
    
    # Generate automaton
    data = myrule.N_Gens(initial_state, args.boundary, args.generations)
    
    # Visualize
    print(f"\nRule {args.rule}, {args.boundary} boundary, {args.generations} generations:")
    visualize_eca(data, mode=args.mode, downsample=args.downsample, 
                  output_file=args.output, boundary=args.boundary, rule=args.rule)

# If invoked as a script
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        # Provide usage instructions if no arguments given
        print("Elementary Cellular Automaton Generator")
        print("\nUsage examples:")
        print("  python3 Generate_ECA.py --rule 110 --generations 50 --mode ascii")
        print("  python3 Generate_ECA.py --rule 30 --generations 100 --init center --width 80")
        print("  python3 Generate_ECA.py --rule 90 --generations 75 --init custom --custom 010101")
        print("  python3 Generate_ECA.py --rule 110 --generations 50 --mode html --output rule110.html")
        print("  python3 Generate_ECA.py --rule 30 --generations 60 --mode 3d --output rule30_cylinder.html")
        print("\nRequired arguments:")
        print("  --rule NUMBER         Rule number (0-255)")
        print("  --generations NUMBER  Number of generations to run")
        print("\nOptional arguments:")
        print("  --boundary TYPE       Boundary condition: 'periodic' or 'null' (default: periodic)")
        print("  --init TYPE           Initial state: 'random', 'center', or 'custom' (default: random)")
        print("  --width NUMBER        Width for random or center init (default: 100)")
        print("  --custom STRING       Custom initial state (binary string, required if --init=custom)")
        print("  --mode TYPE           Visualization: 'ascii', 'html', 'ppm', '3d' (default: ascii)")
        print("                        Note: '3d' mode only works with periodic boundary conditions")
        print("  --downsample NUMBER   Downsample factor (default: 1)")
        print("  --output FILENAME     Output file name (if not provided, displays in console for ascii)")