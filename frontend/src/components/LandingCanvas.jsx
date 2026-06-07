import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function LandingCanvas() {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    // 1. Scene & Camera Setup
    const scene = new THREE.Scene();
    // Add dark compiler fog for depth
    scene.fog = new THREE.FogExp2(0x0a0a0c, 0.015);

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.z = 45;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.appendChild(renderer.domElement);

    // 2. Groups
    const group = new THREE.Group();
    scene.add(group);

    // 3. Create AST Network Nodes
    const nodeCount = 80;
    const positions = new Float32Array(nodeCount * 3);
    const nodes = [];

    // Generate random hierarchical-like positions (layered)
    for (let i = 0; i < nodeCount; i++) {
      // Layer nodes based on index to simulate compiler stages (left to right / top to bottom)
      const layer = Math.floor(i / (nodeCount / 4)); // 4 main stages
      const x = (layer - 1.5) * 20 + (Math.random() - 0.5) * 8;
      const y = (Math.random() - 0.5) * 20;
      const z = (Math.random() - 0.5) * 12;

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      nodes.push({
        x, y, z,
        originX: x, originY: y, originZ: z,
        speed: 0.1 + Math.random() * 0.2,
        phase: Math.random() * Math.PI * 2
      });
    }

    // 4. Create Node Points (Glowing dots)
    const nodeGeometry = new THREE.BufferGeometry();
    nodeGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    // Custom shader material for glowing circular points
    const particleTexture = createCircleTexture();
    const nodeMaterial = new THREE.PointsMaterial({
      color: 0x60a5fa,
      size: 0.8,
      map: particleTexture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const nodePoints = new THREE.Points(nodeGeometry, nodeMaterial);
    group.add(nodePoints);

    // 5. Connect Nodes with Lines (representing parsing channels)
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x1e293b,
      transparent: true,
      opacity: 0.35,
      blending: THREE.AdditiveBlending
    });

    const linePositions = [];
    const connections = [];

    // Establish links between nearby nodes or logical layers
    for (let i = 0; i < nodeCount; i++) {
      let connectionsCount = 0;
      for (let j = i + 1; j < nodeCount; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dz = nodes[i].z - nodes[j].z;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        // Connect if close enough and not too many connections
        if (dist < 12 && connectionsCount < 3) {
          linePositions.push(nodes[i].x, nodes[i].y, nodes[i].z);
          linePositions.push(nodes[j].x, nodes[j].y, nodes[j].z);
          connections.push({ from: i, to: j, dist });
          connectionsCount++;
        }
      }
    }

    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    const networkLines = new THREE.LineSegments(lineGeometry, lineMaterial);
    group.add(networkLines);

    // 6. Flying "Token" Packets
    const packetCount = 25;
    const packetGroup = new THREE.Group();
    group.add(packetGroup);

    const packets = [];
    const packetMaterial = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending
    });
    const packetGeometry = new THREE.SphereGeometry(0.18, 8, 8);

    for (let i = 0; i < packetCount; i++) {
      if (connections.length === 0) break;
      const connection = connections[Math.floor(Math.random() * connections.length)];
      const mesh = new THREE.Mesh(packetGeometry, packetMaterial);
      packetGroup.add(mesh);

      packets.push({
        mesh,
        connection,
        progress: Math.random(),
        speed: 0.003 + Math.random() * 0.005
      });
    }

    // 7. Ambient Background Starfield (Subtle compiler noise)
    const starCount = 300;
    const starPositions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      starPositions[i * 3] = (Math.random() - 0.5) * 150;
      starPositions[i * 3 + 1] = (Math.random() - 0.5) * 150;
      starPositions[i * 3 + 2] = (Math.random() - 0.5) * 150;
    }
    const starGeometry = new THREE.BufferGeometry();
    starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    const starMaterial = new THREE.PointsMaterial({
      color: 0x475569,
      size: 0.35,
      transparent: true,
      opacity: 0.6,
      depthWrite: false
    });
    const starPoints = new THREE.Points(starGeometry, starMaterial);
    scene.add(starPoints);

    // 8. Mouse Interactions
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const onMouseMove = (event) => {
      mouseX = (event.clientX - width / 2) / 80;
      mouseY = (event.clientY - height / 2) / 80;
    };

    window.addEventListener('mousemove', onMouseMove);

    // 9. Animation Loop
    let clock = new THREE.Clock();
    let animationFrameId;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      // Inertia tracking for mouse
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;

      // Rotate network based on mouse
      group.rotation.y = targetX * 0.4 + time * 0.02;
      group.rotation.x = targetY * 0.3 + time * 0.01;

      // Animate nodes dynamically (floating wave effect)
      const positionsAttr = nodeGeometry.attributes.position;
      for (let i = 0; i < nodeCount; i++) {
        const n = nodes[i];
        n.phase += delta * n.speed;
        
        // Soft float
        const currentY = n.originY + Math.sin(n.phase) * 0.4;
        const currentZ = n.originZ + Math.cos(n.phase) * 0.3;

        positionsAttr.setY(i, currentY);
        positionsAttr.setZ(i, currentZ);

        // Update active values
        n.y = currentY;
        n.z = currentZ;
      }
      positionsAttr.needsUpdate = true;

      // Move lines with the floating nodes
      const linePositionsAttr = lineGeometry.attributes.position;
      let lineIndex = 0;
      for (let k = 0; k < connections.length; k++) {
        const conn = connections[k];
        const fromNode = nodes[conn.from];
        const toNode = nodes[conn.to];

        linePositionsAttr.setXYZ(lineIndex++, fromNode.x, fromNode.y, fromNode.z);
        linePositionsAttr.setXYZ(lineIndex++, toNode.x, toNode.y, toNode.z);
      }
      linePositionsAttr.needsUpdate = true;

      // Animate packet transmission
      for (let i = 0; i < packets.length; i++) {
        const p = packets[i];
        p.progress += p.speed;

        if (p.progress >= 1.0) {
          p.progress = 0;
          p.connection = connections[Math.floor(Math.random() * connections.length)];
        }

        const fromNode = nodes[p.connection.from];
        const toNode = nodes[p.connection.to];

        // Interpolate position along connection path
        p.mesh.position.x = fromNode.x + (toNode.x - fromNode.x) * p.progress;
        p.mesh.position.y = fromNode.y + (toNode.y - fromNode.y) * p.progress;
        p.mesh.position.z = fromNode.z + (toNode.z - fromNode.z) * p.progress;
      }

      renderer.render(scene, camera);
    };

    animate();

    // 10. Resize handler
    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    // Clean up function
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      scene.clear();
      renderer.dispose();
    };
  }, []);

  // Programmatically create circular glowing texture to avoid external assets
  function createCircleTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');

    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(0.2, 'rgba(186, 230, 253, 0.8)');
    gradient.addColorStop(0.5, 'rgba(56, 189, 248, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);

    return new THREE.CanvasTexture(canvas);
  }

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full pointer-events-none select-none z-0"
      style={{ background: 'radial-gradient(circle at center, #111317 0%, #08090d 100%)' }}
    />
  );
}
