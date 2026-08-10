<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  file: {
    type: Object,
    required: true,
  },
  resolution: {
    type: Number,
    default: 256,
  },
})

const emit = defineEmits(['failed'])
const imageRef = ref(null)
const canvasRef = ref(null)
const imageAspectRatio = ref('1 / 1')
let animationFrame = 0
let objectUrl = null
let context = null

function stopAnimation() {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
    animationFrame = 0
  }
}

function resetCanvas() {
  stopAnimation()
  if (context && canvasRef.value) {
    context.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  }
  context = null
}

function buildEdgeMap(image, width, height) {
  const offscreen = document.createElement('canvas')
  offscreen.width = width
  offscreen.height = height
  const offscreenContext = offscreen.getContext('2d', { willReadFrequently: true })
  if (!offscreenContext) throw new Error('Unable to create image-processing canvas')

  offscreenContext.drawImage(image, 0, 0, width, height)
  const { data } = offscreenContext.getImageData(0, 0, width, height)
  const grayscale = new Float32Array(width * height)
  const edges = new Float32Array(width * height)
  const seeds = []

  for (let index = 0; index < grayscale.length; index += 1) {
    const pixel = index * 4
    grayscale[index] = data[pixel] * 0.299 + data[pixel + 1] * 0.587 + data[pixel + 2] * 0.114
  }

  for (let y = 1; y < height - 1; y += 1) {
    for (let x = 1; x < width - 1; x += 1) {
      const top = (y - 1) * width + x
      const middle = y * width + x
      const bottom = (y + 1) * width + x
      const gx = -grayscale[top - 1] + grayscale[top + 1]
        - 2 * grayscale[middle - 1] + 2 * grayscale[middle + 1]
        - grayscale[bottom - 1] + grayscale[bottom + 1]
      const gy = -grayscale[top - 1] - 2 * grayscale[top] - grayscale[top + 1]
        + grayscale[bottom - 1] + 2 * grayscale[bottom] + grayscale[bottom + 1]
      const magnitude = Math.hypot(gx, gy)
      edges[middle] = magnitude
      if (magnitude > 80) seeds.push({ x, y })
    }
  }

  return { edges, seeds }
}

function createWalker(seeds, width, height) {
  const seed = seeds[Math.floor(Math.random() * seeds.length)]
  return {
    x: seed.x,
    y: seed.y,
    life: 20 + Math.floor(Math.random() * Math.min(400, width)),
    visited: new Set(),
    width,
    height,
  }
}

function stepWalker(walker, edges, drawContext) {
  if (walker.life <= 0) return false

  let bestMagnitude = 20
  let nextX = walker.x
  let nextY = walker.y

  for (let dy = -1; dy <= 1; dy += 1) {
    for (let dx = -1; dx <= 1; dx += 1) {
      if (dx === 0 && dy === 0) continue
      const x = walker.x + dx
      const y = walker.y + dy
      if (x < 1 || x >= walker.width - 1 || y < 1 || y >= walker.height - 1) continue
      const key = y * walker.width + x
      if (!walker.visited.has(key) && edges[key] > bestMagnitude) {
        bestMagnitude = edges[key]
        nextX = x
        nextY = y
      }
    }
  }

  if (nextX === walker.x && nextY === walker.y) return false

  drawContext.beginPath()
  drawContext.moveTo(walker.x, walker.y)
  drawContext.lineTo(nextX, nextY)
  drawContext.stroke()
  walker.visited.add(nextY * walker.width + nextX)
  walker.x = nextX
  walker.y = nextY
  walker.life -= 1
  return true
}

function startAnimation(image) {
  resetCanvas()
  const canvas = canvasRef.value
  const longestSide = Math.max(image.naturalWidth, image.naturalHeight)
  const scale = Math.min(1, Math.max(128, props.resolution) / longestSide)
  const width = Math.max(1, Math.round(image.naturalWidth * scale))
  const height = Math.max(1, Math.round(image.naturalHeight * scale))
  imageAspectRatio.value = `${image.naturalWidth} / ${image.naturalHeight}`
  const devicePixelRatio = Math.min(window.devicePixelRatio || 1, 2)
  canvas.width = width * devicePixelRatio
  canvas.height = height * devicePixelRatio
  context = canvas.getContext('2d')
  if (!context) throw new Error('Unable to create trail canvas')
  context.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0)
  context.lineWidth = 1.5
  context.lineCap = 'round'
  context.strokeStyle = '#00ffcc'
  context.shadowColor = '#00ffcc'
  context.shadowBlur = 6

  const { edges, seeds } = buildEdgeMap(image, width, height)
  if (!seeds.length) throw new Error('No usable image edges found')

  const walkerCount = width >= 512 ? 30 : 16
  const walkers = Array.from({ length: walkerCount }, () => createWalker(seeds, width, height))
  const fadeStyle = 'rgba(10, 10, 12, 0.025)'

  const animate = () => {
    if (!context) return
    context.fillStyle = fadeStyle
    context.fillRect(0, 0, width, height)
    walkers.forEach((walker, index) => {
      if (!stepWalker(walker, edges, context)) {
        walkers[index] = createWalker(seeds, width, height)
      }
    })
    animationFrame = requestAnimationFrame(animate)
  }

  animate()
}

function handleImageLoad() {
  try {
    startAnimation(imageRef.value)
  } catch {
    emit('failed')
  }
}

function handleImageError() {
  emit('failed')
}

function loadImage() {
  resetCanvas()
  if (objectUrl) URL.revokeObjectURL(objectUrl)
  objectUrl = URL.createObjectURL(props.file)
  if (imageRef.value) {
    imageRef.value.src = objectUrl
  }
}

onMounted(loadImage)
watch(() => props.file, loadImage)
onBeforeUnmount(() => {
  resetCanvas()
  if (objectUrl) URL.revokeObjectURL(objectUrl)
})
</script>

<template>
  <div class="particle-walker" :style="{ aspectRatio: imageAspectRatio }" aria-hidden="true">
    <img ref="imageRef" class="particle-walker__image" alt="" @load="handleImageLoad" @error="handleImageError" />
    <canvas ref="canvasRef" class="particle-walker__canvas" />
  </div>
</template>

<style scoped>
.particle-walker {
  position: relative;
  width: min(100%, 560px);
  aspect-ratio: 1 / 1;
  overflow: hidden;
  background: #0a0a0c;
  box-shadow: 0 0 32px color-mix(in srgb, #00ffcc 16%, transparent);
}

.particle-walker__image,
.particle-walker__canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.particle-walker__image {
  object-fit: cover;
  opacity: 0.98;
}

.particle-walker__canvas {
  pointer-events: none;
}

@media (max-width: 600px) {
  .particle-walker {
    width: min(100%, 360px);
  }
}
</style>
