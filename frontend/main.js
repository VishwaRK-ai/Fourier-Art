// const canvas = document.getElementById("canvas");
// const ctx = canvas.getContext("2d");

// let fourier = [];
// let path = [];
// let time = 0;
// let K = 200;

// document.getElementById("kSlider").oninput = e => {
//   K = parseInt(e.target.value);
//   document.getElementById("kVal").innerText = K;
//   reset();
// };

// document.getElementById("upload").onchange = async e => {
//   const form = new FormData();
//   form.append("image", e.target.files[0]);

//   const res = await fetch("http://127.0.0.1:5000/upload", {
//     method: "POST",
//     body: form
//   });

//   const data = await res.json();
//   fourier = data.fourier;

//   fourier.sort((a, b) =>
//     Math.hypot(b.re, b.im) - Math.hypot(a.re, a.im)
//   );

//   reset();
// };

// function reset() {
//   path = [];
//   time = 0;
// }

// function drawEpicycles(x, y, rotation) {
//   for (let i = 0; i < K; i++) {
//     const prevx = x;
//     const prevy = y;

//     const freq = fourier[i].freq;
//     const re = fourier[i].re;
//     const im = fourier[i].im;

//     const radius = Math.hypot(re, im);
//     const angle = 2 * Math.PI * freq * time + rotation;

//     x += re * Math.cos(angle) - im * Math.sin(angle);
//     y += re * Math.sin(angle) + im * Math.cos(angle);

//     ctx.strokeStyle = "rgba(255,255,255,0.25)";
//     ctx.beginPath();
//     ctx.arc(prevx, prevy, radius, 0, Math.PI * 2);
//     ctx.stroke();

//     ctx.beginPath();
//     ctx.moveTo(prevx, prevy);
//     ctx.lineTo(x, y);
//     ctx.stroke();
//   }

//   return { x, y };
// }

// function animate() {
//   ctx.clearRect(0, 0, canvas.width, canvas.height);
//   ctx.save();
//   ctx.translate(canvas.width / 2, canvas.height / 2);
//   ctx.scale(1, -1); // FIX inversion

//   const p = drawEpicycles(0, 0, 0);
//   path.push(p);

//   ctx.strokeStyle = "#00ffff";
//   ctx.beginPath();
//   ctx.moveTo(path[0].x, path[0].y);
//   for (let i = 1; i < path.length; i++) {
//     ctx.lineTo(path[i].x, path[i].y);
//   }
//   ctx.stroke();

//   ctx.restore();

//   time += 1 / fourier.length;
//   requestAnimationFrame(animate);
// }

// animate();