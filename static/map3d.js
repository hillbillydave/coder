// static/map3d.js
const sceneObjects = {}; 
let scene, camera, renderer;
let trackedObjectId = null;
const homePosition = new THREE.Vector3(0, 700, 1200);
const textureLoader = new THREE.TextureLoader();
let availableTextures = {};
let plottedPathLine = null;
let selectionBox; 
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const keyState = {};
const mouseState = { isDown: false };
const cameraRotation = new THREE.Euler(0, 0, 0, 'YXZ');
const ZOOM_SPEED = 5;
let asteroidInstancedMesh;
const asteroidCount = 2000;
const dummy = new THREE.Object3D();

window.updateMap = updateMap;
window.updatePlottedPath = updatePlottedPath;
window.trackObjectById = (id) => { trackedObjectId = id; };
window.goHome = () => { trackedObjectId = null; };

async function init3DMap() {
    const container = document.getElementById("map3d");
    if (!container || container.childElementCount !== 0) return;
    try {
        const response = await fetch("/get_texture_info");
        availableTextures = await response.json();
    } catch (error) { console.error("Could not fetch texture info:", error); }

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 50000);
    camera.position.copy(homePosition);

    if (availableTextures.starfield) {
        const sphereGeo = new THREE.SphereGeometry(20000, 64, 64);
        const sphereMat = new THREE.MeshBasicMaterial({ map: textureLoader.load(availableTextures.starfield), side: THREE.BackSide });
        scene.add(new THREE.Mesh(sphereGeo, sphereMat));
    }

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(window.devicePixelRatio * 0.9);
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0x888888);
    const pointLight = new THREE.PointLight(0xffffff, 1.5, 80000);
    scene.add(ambientLight, pointLight);
    
    selectionBox = new THREE.BoxHelper(new THREE.Mesh(), 0xffff00);
    selectionBox.visible = false;
    scene.add(selectionBox);

    const asteroidGeometry = new THREE.IcosahedronGeometry(1, 0);
    const asteroidMaterial = new THREE.MeshStandardMaterial({ color: 0x888888 });
    asteroidInstancedMesh = new THREE.InstancedMesh(asteroidGeometry, asteroidMaterial, asteroidCount);
    scene.add(asteroidInstancedMesh);

    container.addEventListener('click', onObjectClick);
    window.addEventListener('keydown', (event) => keyState[event.code] = true);
    window.addEventListener('keyup', (event) => keyState[event.code] = false);
    container.addEventListener('mousedown', (event) => { mouseState.isDown = true; mouseState.lastX = event.clientX; mouseState.lastY = event.clientY; });
    window.addEventListener('mouseup', () => mouseState.isDown = false);
    window.addEventListener('mousemove', (event) => {
        if (!mouseState.isDown) return;
        if (trackedObjectId) { trackedObjectId = null; }
        const deltaX = event.clientX - mouseState.lastX;
        const deltaY = event.clientY - mouseState.lastY;
        cameraRotation.y -= deltaX * 0.005;
        cameraRotation.x -= deltaY * 0.005;
        cameraRotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, cameraRotation.x));
        mouseState.lastX = event.clientX;
        mouseState.lastY = event.clientY;
    });
    container.addEventListener('wheel', (event) => {
        const direction = new THREE.Vector3();
        camera.getWorldDirection(direction);
        camera.position.addScaledVector(direction, -event.deltaY * ZOOM_SPEED);
    });

    animate();
}

function animate() {
    requestAnimationFrame(animate);
    const moveVector = new THREE.Vector3();
    if (keyState.KeyW) moveVector.z -= 1;
    if (keyState.KeyS) moveVector.z += 1;
    if (keyState.KeyA) moveVector.x -= 1;
    if (keyState.KeyD) moveVector.x += 1;
    if (keyState.KeyE) moveVector.y += 1;
    if (keyState.KeyQ) moveVector.y -= 1;
    if (moveVector.lengthSq() > 0) { trackedObjectId = null; }
    if (trackedObjectId && sceneObjects[trackedObjectId]) {
        const targetObject = sceneObjects[trackedObjectId];
        const offset = new THREE.Vector3(0, targetObject.userData.size * 3, targetObject.userData.size * 8);
        camera.position.lerp(offset.add(targetObject.position), 0.05);
        camera.lookAt(targetObject.position);
    } else {
        camera.rotation.copy(cameraRotation);
        moveVector.applyEuler(camera.rotation);
        camera.position.addScaledVector(moveVector, 10);
    }

    const SCENE_SCALE_AU = 150.0;
    const time = Date.now() * 0.0001;
    
    if (asteroidInstancedMesh && asteroidInstancedMesh.userData.asteroids) {
        asteroidInstancedMesh.userData.asteroids.forEach((asteroidData, i) => {
            const oe = asteroidData.orbital_elements;
            const mean_anomaly = (oe.mean_anomaly + time * (2 * Math.PI / oe.period)) % (2 * Math.PI);
            const r = oe.semi_major_axis * (1 - oe.eccentricity**2) / (1 + oe.eccentricity * Math.cos(mean_anomaly));
            const x2d = r * Math.cos(mean_anomaly);
            const z2d = r * Math.sin(mean_anomaly);
            
            dummy.position.set(x2d * SCENE_SCALE_AU, z2d * Math.sin(oe.inclination) * SCENE_SCALE_AU, z2d * Math.cos(oe.inclination) * SCENE_SCALE_AU);
            dummy.scale.set(asteroidData.size, asteroidData.size, asteroidData.size);
            dummy.updateMatrix();
            asteroidInstancedMesh.setMatrixAt(i, dummy.matrix);
        });
        asteroidInstancedMesh.instanceMatrix.needsUpdate = true;
    }

    renderer.render(scene, camera);
}

function updateMap(orbitalData) {
    if (!scene) return;
    const existingObjectIds = new Set(Object.keys(sceneObjects));
    
    const asteroids = orbitalData.filter(d => d.type === 'asteroid');
    const otherObjects = orbitalData.filter(d => d.type !== 'asteroid');
    const incomingObjectIds = new Set(otherObjects.map(obj => obj.id));

    if (asteroidInstancedMesh && asteroids.length > 0) {
        asteroidInstancedMesh.userData.asteroids = asteroids;
    }

    otherObjects.forEach(objData => {
        let sceneObj = sceneObjects[objData.id];
        if (!sceneObj) {
            let geometry, material;
            if (objData.type === 'neo') {
                geometry = new THREE.IcosahedronGeometry(objData.size, 0); 
            } else {
                geometry = new THREE.SphereGeometry(objData.size, 32, 32);
            }
            if (objData.id === 'earth' && availableTextures.earth) {
                 material = new THREE.MeshStandardMaterial({ map: textureLoader.load(availableTextures.earth) });
            } else {
                const texture = availableTextures[objData.id] ? textureLoader.load(availableTextures[objData.id]) : null;
                if (texture) {
                    material = (objData.type === 'star') ?
                        new THREE.MeshBasicMaterial({ map: texture }) :
                        new THREE.MeshStandardMaterial({ map: texture });
                } else {
                    let color = 0x8B5CF6;
                    if (objData.type === 'planet') color = 0x4d7cff;
                    if (objData.type === 'star') color = 0xFFD700;
                    if (objData.type === 'satellite') color = 0xFFFFFF;
                    material = new THREE.MeshStandardMaterial({ color: color });
                }
            }
            sceneObj = new THREE.Mesh(geometry, material);
            sceneObj.name = objData.id;
            sceneObjects[objData.id] = sceneObj;
            scene.add(sceneObj);
            if (objData.id === 'saturn' && availableTextures.saturn_ring) {
                const ringGeo = new THREE.RingGeometry(objData.size * 1.5, objData.size * 2.5, 64);
                const ringMat = new THREE.MeshBasicMaterial({ map: textureLoader.load(availableTextures.saturn_ring), side: THREE.DoubleSide, transparent: true });
                const ringMesh = new THREE.Mesh(ringGeo, ringMat);
                ringMesh.rotation.x = -Math.PI / 2;
                sceneObj.add(ringMesh);
            }
        }
        sceneObj.userData = objData;
        sceneObj.position.set(objData.position.x, objData.position.y, objData.position.z);
        if (objData.type !== 'star') { sceneObj.rotation.y += 0.001; }
        if (objData.type === 'satellite') { sceneObj.material.color.setHex(objData.status === 'Anomaly Detected' ? 0xff3344 : 0xffffff); }
        if (objData.type === 'neo') { sceneObj.material.color.setHex(objData.is_hazardous ? 0xff3344 : 0xffaa00); }
    });

    existingObjectIds.forEach(id => {
        if (!incomingObjectIds.has(id)) {
            const objectToRemove = sceneObjects[id];
            scene.remove(objectToRemove);
            delete sceneObjects[id];
        }
    });
}

// --- THIS IS THE RESTORED SELECTION LOGIC ---
function onObjectClick(event) {
    event.preventDefault();
    mouse.x = (event.clientX / renderer.domElement.clientWidth) * 2 - 1;
    mouse.y = -(event.clientY / renderer.domElement.clientHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    
    // The raycaster now correctly checks ALL scene objects
    const intersects = raycaster.intersectObjects(scene.children, true);
    
    if (intersects.length > 0) {
        let selectedObject = null;
        // Find the first object that isn't the starfield or selection box
        for (const intersect of intersects) {
            if (intersect.object.type === 'Mesh' && intersect.object.geometry.type !== 'SphereGeometry') {
                selectedObject = intersect.object;
                break;
            }
        }
        updateSelectionInfo(selectedObject);
    } else {
        updateSelectionInfo(null);
    }
}

function updateSelectionInfo(selectedObject) {
    const infoPanel = document.getElementById('selection-info');
    const plotterInput = document.getElementById('objectIdInput');
    if (selectedObject && selectedObject.userData && selectedObject.userData.id) {
        const data = selectedObject.userData;
        let html = `<h3>${data.name || data.id}</h3><p>Type: ${data.type}</p>`;
        if (data.type === 'neo') {
            html += `<p>Hazardous: <span class="${data.is_hazardous ? 'status-bad' : 'status-ok'}">${data.is_hazardous}</span></p>`;
            html += `<p>Velocity: ${data.velocity_kps} kps</p><p>Miss Distance: ${data.miss_distance_km}</p>`;
        }
        infoPanel.innerHTML = html;
        plotterInput.value = data.name || data.id;
        selectionBox.setFromObject(selectedObject);
        selectionBox.visible = true;
    } else {
        infoPanel.innerHTML = 'Awaiting Selection...';
        plotterInput.value = '';
        selectionBox.visible = false;
    }
}

function updatePlottedPath(data) {
    if (data && data.path && data.path.length > 0) {
        if (window.handleStatusUpdate) window.handleStatusUpdate(`Path received for ${data.id}. Rendering...`);
        if (plottedPathLine) { scene.remove(plottedPathLine); plottedPathLine.geometry.dispose(); plottedPathLine.material.dispose(); }
        const points = data.path.map(p => new THREE.Vector3(p.x, p.y, p.z));
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ color: 0xff00ff });
        plottedPathLine = new THREE.Line(geometry, material);
        scene.add(plottedPathLine);
        if (window.handleStatusUpdate) window.handleStatusUpdate(`Render complete for ${data.id}.`);
    } else if (data && data.error) {
        if (window.handleStatusUpdate) window.handleStatusUpdate(`Error: ${data.error}`);
    }
}
// --- END OF RESTORATION ---

document.addEventListener('DOMContentLoaded', init3DMap);
