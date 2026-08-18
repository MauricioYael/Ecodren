// ═══════════════════════════════════════════
//   CONFIGURACIÓN ESCENARIO 3D - ECODREN 2026
// ═══════════════════════════════════════════

(function() {
  const heroContainer = document.getElementById('hero3d');
  const heroCanvas = document.getElementById('hero-canvas');
  if (!heroContainer || !heroCanvas) return;

  // 1. ESCENA, CÁMARA Y RENDERER
  const ecoScene = new THREE.Scene();
  const ecoCamera = new THREE.PerspectiveCamera(45, heroContainer.clientWidth / heroContainer.clientHeight, 0.1, 100);
  
  ecoCamera.position.set(0, 0, 8); 

  const ecoRenderer = new THREE.WebGLRenderer({ 
    canvas: heroCanvas, 
    antialias: true,
    alpha: true
  });
  ecoRenderer.setSize(heroContainer.clientWidth, heroContainer.clientHeight);
  ecoRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  ecoRenderer.shadowMap.enabled = true;
  ecoRenderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // GRUPO INTERACTIVO
  const interactiveGroup = new THREE.Group();
  ecoScene.add(interactiveGroup);

  // 2. LUCES DEL ESCENARIO
  const ambientLight = new THREE.AmbientLight(0x2a353d, 1.4);
  ecoScene.add(ambientLight);

  const sunLight = new THREE.DirectionalLight(0xffffff, 2.5);
  sunLight.position.set(10, 15, 8);
  sunLight.castShadow = true;
  ecoScene.add(sunLight);

  const limeReflector = new THREE.PointLight(0xbffd00, 3.5, 25); 
  limeReflector.position.set(5, 5, 6);
  ecoScene.add(limeReflector);

  const orangeReflector = new THREE.PointLight(0xe85c1a, 1.5, 12);
  orangeReflector.position.set(-4, 2, -3);
  ecoScene.add(orangeReflector);

  // 3. PISO INDUSTRIAL
  const ecoGround = new THREE.Mesh(
    new THREE.CircleGeometry(14, 64),
    new THREE.MeshStandardMaterial({ color: 0x111618, roughness: 1 })
  );
  ecoGround.rotation.x = -Math.PI / 2;
  ecoGround.position.y = -3.0;
  ecoGround.receiveShadow = true;
  ecoScene.add(ecoGround);

  // 4. PARTÍCULAS FLOTANTES (Chispas)
  const particleGeo = new THREE.BufferGeometry();
  const particleCount = 120;
  const posArray = new Float32Array(particleCount * 3);
  for (let i = 0; i < particleCount * 3; i += 3) {
    posArray[i] = (Math.random() - 0.5) * 15;     
    posArray[i + 1] = (Math.random() - 0.5) * 10; 
    posArray[i + 2] = (Math.random() - 0.5) * 15; 
  }
  particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
  const sparkParticles = new THREE.Points(
    particleGeo, 
    new THREE.PointsMaterial({ color: 0xbffd00, size: 0.04, transparent: true, opacity: 0.35 })
  );
  ecoScene.add(sparkParticles);

  // 5. CARGADOR DINÁMICO DEL MODELO 3D (.GLB)
  let realLogoMesh = null; 
  const gltfLoader = new THREE.GLTFLoader();

  // 🚀 Leemos la ruta estática resuelta por Django en el HTML
  const modelUrl = heroCanvas.getAttribute('data-model') || '/static/Assets/logo-web.glb';

  gltfLoader.load(
    modelUrl, 
    function (gltf) {
      const modelContainer = new THREE.Group();
      const loadedModel = gltf.scene;
      
      loadedModel.traverse(function (node) {
        if (node.isMesh) {
          node.castShadow = true;
          node.receiveShadow = true;
          if(node.material) {
            node.material.color.set(0xccff00); 
            node.material.roughness = 0.3;     
            node.material.metalness = 0.40;    
          }
        }
      });

      while (loadedModel.children.length > 0) {
        modelContainer.add(loadedModel.children[0]);
      }

      modelContainer.scale.set(5, 5, 5);       
      modelContainer.rotation.set(Math.PI / 2, 0, 0); 

      const box = new THREE.Box3().setFromObject(modelContainer);
      const center = new THREE.Vector3();
      box.getCenter(center);
      modelContainer.position.sub(center);

      const pivot = new THREE.Group();
      pivot.position.set(0, -1.5, 0); 
      pivot.add(modelContainer);

      realLogoMesh = pivot;
      ecoScene.add(realLogoMesh);
      console.log("✔ Modelo 3D cargado correctamente desde:", modelUrl);
    },
    undefined,
    function (error) {
      console.error('Error al cargar el archivo .glb:', error, 'Ruta intentada:', modelUrl);
    }
  );

  // 6. BUCLE DE ANIMACIÓN
  const ecoClock = new THREE.Clock();

  function runAnimation() {
    requestAnimationFrame(runAnimation);
    
    if (realLogoMesh) {
      realLogoMesh.rotation.z -= 0.01; 
      realLogoMesh.rotation.x = 0;
      realLogoMesh.rotation.y = 0;
    }

    sparkParticles.rotation.y = ecoClock.getElapsedTime() * 0.015;
    ecoRenderer.render(ecoScene, ecoCamera);
  }
  runAnimation();

  // 7. DISEÑO RESPONSIVO
  window.addEventListener('resize', () => {
    ecoCamera.aspect = heroContainer.clientWidth / heroContainer.clientHeight;
    ecoCamera.updateProjectionMatrix();
    ecoRenderer.setSize(heroContainer.clientWidth, heroContainer.clientHeight);
  });
})();