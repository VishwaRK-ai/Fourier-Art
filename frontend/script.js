const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
    canvas.width = window.innerWidth - 300;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

let coords = [];
let fourier = [];
let path = [];
let time = 0;

let K = 200;
let scale = 1;
let speed = 1;

let drawLineWidth = 2;
let circleLineWidth = 1;
let pathColor = "#ff0080";
let circleColor = "#00ffea";
let fadeStrength = 0.25;

let cameraMode = "static";
let camX = 0;
let camY = 0;

const kSlider = document.getElementById("kSlider");
const scaleSlider = document.getElementById("scaleSlider");
const speedSlider = document.getElementById("speedSlider");
const imageInput = document.getElementById("imageInput");
const uploadStatus = document.getElementById("uploadStatus");
const uploadedImage = document.getElementById("uploadedImage");
// NEW: Select contour elements
const contourImage = document.getElementById("contourImage");
const contourContainer = document.getElementById("contourContainer");

const drawWidthSlider = document.getElementById("drawWidthSlider");
const circleWidthSlider = document.getElementById("circleWidthSlider");
const pathColorPicker = document.getElementById("pathColorPicker");
const circleColorPicker = document.getElementById("circleColorPicker");
const fadeSlider = document.getElementById("fadeSlider");

const camStaticBtn = document.getElementById("camStatic");
const camFollowBtn = document.getElementById("camFollow");

camStaticBtn.onclick = () => {
    cameraMode = "static";
    camStaticBtn.classList.add("active");
    camFollowBtn.classList.remove("active");
};

camFollowBtn.onclick = () => {
    cameraMode = "follow";
    camFollowBtn.classList.add("active");
    camStaticBtn.classList.remove("active");
};

imageInput.addEventListener("change", async () => {
    const file = imageInput.files[0];
    if (!file) return;

    uploadedImage.src = URL.createObjectURL(file);
    uploadedImage.style.display = "block";
    
    // NEW: Hide contour preview while uploading new image
    contourContainer.style.display = "none";
    
    uploadStatus.textContent = "Uploading: " + file.name + "...";

    const formData = new FormData();
    formData.append("image", file);

    await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData
    });

    uploadStatus.textContent = "Uploaded: " + file.name;

    fetchCoords();
});

async function fetchCoords() {
    const res = await fetch("http://127.0.0.1:5000/coords");
    const data = await res.json();
    if (data.error) return;

    // NEW: Show contour image if available
    if (data.contour_image) {
        contourImage.src = data.contour_image;
        contourContainer.style.display = "block";
    }

    coords = data.coords.map(c => ({ re: c.re, im: c.im }));

    let mr = 0, mi = 0;
    coords.forEach(c => { mr += c.re; mi += c.im; });
    mr /= coords.length;
    mi /= coords.length;

    coords = coords.map(c => ({ re: c.re - mr, im: c.im - mi }));
    computeFourier();
}

function computeFourier() {
    const N = coords.length;
    fourier = [];
    path = [];
    time = 0;

    for (let k = -Math.floor(N/2); k < Math.floor(N/2); k++) {
        let sr = 0, si = 0;
        for (let n = 0; n < N; n++) {
            const phi = -2 * Math.PI * k * n / N;
            sr += coords[n].re * Math.cos(phi) - coords[n].im * Math.sin(phi);
            si += coords[n].re * Math.sin(phi) + coords[n].im * Math.cos(phi);
        }
        sr /= N;
        si /= N;
        fourier.push({
            re: sr,
            im: si,
            freq: k,
            amp: Math.hypot(sr, si),
            phase: Math.atan2(si, sr)
        });
    }

    fourier.sort((a,b) => b.amp - a.amp);
    fourier = fourier.slice(0, K);
}

function drawEpicycles(x, y) {
    for (const f of fourier) {
        const px = x;
        const py = y;
        const a = f.phase + 2 * Math.PI * f.freq * time;
        x += f.amp * Math.cos(a);
        y += f.amp * Math.sin(a);

        ctx.strokeStyle = "rgba(255,255,255,0.25)";
        ctx.lineWidth = circleLineWidth;
        ctx.beginPath();
        ctx.arc(px, py, f.amp, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = circleColor;
        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(x, y);
        ctx.stroke();
    }
    return { x, y };
}

function animate() {
    ctx.fillStyle = `rgba(17,17,17,${1 - fadeStrength})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (coords.length) {
        ctx.save();

        if (cameraMode === "follow" && path.length) {
            camX += (path[0].x - camX) * 0.05;
            camY += (path[0].y - camY) * 0.05;
        } else {
            camX = 0;
            camY = 0;
        }

        ctx.translate(
            canvas.width / 2 - camX * scale,
            canvas.height / 2 - camY * scale
        );
        ctx.scale(scale, scale);

        const v = drawEpicycles(0, 0);
        path.unshift(v);

        for (let i = 0; i < path.length - 1; i++) {
            const age = i / path.length;
            const alpha = Math.max(0, 1 - age * 0.5);

            ctx.strokeStyle =
                pathColor + Math.floor(alpha * 255).toString(16).padStart(2, "0");
            ctx.lineWidth = drawLineWidth;

            ctx.beginPath();
            ctx.moveTo(path[i].x, path[i].y);
            ctx.lineTo(path[i + 1].x, path[i + 1].y);
            ctx.stroke();
        }

        ctx.restore();

        time += speed / coords.length;
        if (time > 1) time = 0;
    }

    requestAnimationFrame(animate);
}

kSlider.oninput = () => { K = +kSlider.value; computeFourier(); };
scaleSlider.oninput = () => scale = +scaleSlider.value;
speedSlider.oninput = () => speed = +speedSlider.value;
drawWidthSlider.oninput = () => drawLineWidth = +drawWidthSlider.value;
circleWidthSlider.oninput = () => circleLineWidth = +circleWidthSlider.value;
pathColorPicker.oninput = () => pathColor = pathColorPicker.value;
circleColorPicker.oninput = () => circleColor = circleColorPicker.value;
fadeSlider.oninput = () => fadeStrength = +fadeSlider.value;

fetchCoords();
animate();